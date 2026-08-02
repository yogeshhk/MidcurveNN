# Image-Based (Phase I) Analysis Report

Scope: `src/image_based/` (simpleencoderdecoder, cnnencoderdecoder, denseencoderdecoder,
denoiserencoderdecoder, unet, pix2pix, img2img, testing) plus the shared pipeline files
they consume (`src/config.py`, `src/utils/prepare_data.py`, `src/utils/prepare_plots.py`,
`src/utils/metric_utils.py`). Intentional gotchas documented in `CLAUDE.md` (lazy imports,
`_build()` pattern, unet/test.py import ordering, no `model_from_json`, CI skip guards,
enhanced-alias files) are NOT reported as bugs here.

Date: 2026-07-03.

---

## Overview

All Phase I approaches map a rasterized profile polygon image to a rasterized midcurve
image. Three data products feed them:

- `data/image-pairs/` (896 PNGs = 448 pairs, 100x100 RGBA, geometry stored in the
  ALPHA channel; foreground alpha=255 on transparent background). Consumed by
  simple/cnn/dense/denoiser via `utils/prepare_data.get_training_data`, which extracts
  the alpha channel, giving foreground=1, background=0 after /255. Foreground covers
  only ~0.15% of pixels (measured on `I_Midcurve.png`).
- `data/unet-splits/` (2100 train / 900 test side-by-side 512x256 RGBA PNGs, white
  background, dark strokes). Consumed by `unet/datagenerator.py` via cv2 grayscale
  read: background=1, foreground=0 after /255.
- `data/images-combo/` (268 train / 89 val / 91 test side-by-side JPGs, white
  background, dark strokes). Consumed by pix2pix (Keras) and img2img (PyTorch).

Cross-cutting observations:

1. Class imbalance is the dominant accuracy limiter. Only UNet uses a weighted loss
   (WBCE, beta=0.1). Simple/CNN/Dense/Denoiser use plain BCE on targets where the
   positive class is well under 1% of pixels, so the loss is minimized almost entirely
   by predicting background; predictions come out faint/low-contrast (the per-cell
   autoscale in `prepare_plots.save_results_grid_images` exists precisely to make
   such faint outputs visible).
2. Evaluation is compromised by train/test leakage at two levels: (a) the four
   encoder-decoder mains sample their "test" images from the training arrays; (b) all
   splits (images-combo 60/20/20, unet-splits) are random over AUGMENTED variants
   (rotations/translations/mirrors of the same base shapes), so val/test contain
   near-duplicates of training samples. No approach is evaluated on held-out shapes.
3. The pix2pix and img2img pipelines contain hard crashes and a normalization
   mismatch that makes the Keras GAN unable to ever produce correct output values.
4. There are no quantitative geometry-aware metrics (IoU/Dice/Chamfer/Hausdorff) for
   any image approach; only BCE/accuracy/MAE, and pixel accuracy is ~99% for an
   all-background prediction, so it is uninformative.

---

## Per-Approach Analysis

### 1. simpleencoderdecoder

Architecture: `Dense(10000 -> 100 relu, L1 activity reg, BN, dropout 0.2) ->
Dense(10000, sigmoid)`, BCE loss, Adam(1e-3), 100 epochs, batch 16,
`validation_split=0.3`, EarlyStopping(val_loss, patience=50, restore_best) +
ModelCheckpoint(save_best_only). Data: 100x100 flattened, foreground=1 sparse.

Files: `simpleencoderdecoder/build_simple_encoderdecoder_model.py`,
`main_simple_encoderdecoder.py`.

Issues:
- Plain BCE on ~0.2-1% positive pixels: model is rewarded for predicting near-zero
  everywhere. No class weighting, no Dice.
- Test samples drawn from the training set (`main_simple_encoderdecoder.py:21`).
- 100-unit bottleneck for a 10,000-dim output is extremely aggressive; combined with
  L1 activity regularization it caps achievable detail.
- `build_...py:124` enables `mixed_float16` globally in its `__main__`; float16 BCE
  with sigmoid saturation is a NaN risk on this loss. Minor (main entry point is
  `main_simple_encoderdecoder.py`, which does not set it).

### 2. cnnencoderdecoder

Architecture: 4-level Conv2D encoder (32/64/64/128/128/256/256 with BN) +
Conv2DTranspose decoder levels with additive skip connections, final Conv2D sigmoid.
128x128 input; the main script prepends 2 CoordConv channels (normalized [0,1]) so
input is (128,128,3). BCE loss, `adam`, 15 epochs (quick run), `validation_split=0.2`,
EarlyStopping/ReduceLROnPlateau on TRAIN loss.

Files: `cnnencoderdecoder/build_cnn_encoderdecoder_model.py`,
`main_cnn_encoderdecoder.py`.

Issues:
- Same BCE class-imbalance problem as simple.
- `EarlyStopping(monitor='loss')` and `ReduceLROnPlateau(monitor='loss')`
  (`build_cnn_encoderdecoder_model.py:107-108`) ignore the validation split that is
  computed anyway; `restore_best_weights` restores the best TRAIN loss epoch, which
  encourages overfitting.
- The `__main__` block of `build_cnn_encoderdecoder_model.py:136,147` calls
  `get_training_data` and `plot_results` without importing them (NameError if run
  directly). Dead/broken entry point.
- 100x100 source PNGs are upsampled to 128x128 by `load_img(target_size=(128,128))`
  with default nearest interpolation: 1-px strokes become aliased staircases.
- Test samples drawn from training data (`main_cnn_encoderdecoder.py:25`).
- CoordConv normalization is [0,1] here vs [-1,1] in UNet; harmless but inconsistent.

### 3. denseencoderdecoder

Architecture: `10000 -> 2048 -> 1024 -> 100 -> 1024 -> 2048 -> 10000`, all elu except
final sigmoid. BCE, Adam(1e-4), 100 epochs, `validation_split=0.3`,
EarlyStopping(val_loss, patience=50) WITHOUT `restore_best_weights` and WITHOUT a
ModelCheckpoint.

Files: `denseencoderdecoder/build_dense_encoderdecoder_model.py`,
`main_dense_encoderdecoder.py`.

Issues:
- Same BCE class-imbalance problem.
- `build_dense_encoderdecoder_model.py:76`: when early stopping triggers, the model
  saved at line 89 has the LAST epoch's weights, i.e. up to 50 epochs past the best
  val_loss. Silent quality loss vs the simple variant, which restores best weights.
- Test samples drawn from training data (`main_dense_encoderdecoder.py:22`).

### 4. denoiserencoderdecoder

Architecture: stage 1 = simple encoder-decoder produces noisy midcurves from
profiles (on the full training set); stage 2 = small conv autoencoder
(2x Conv/MaxPool down, 2x Conv/UpSample up, sigmoid) trained to map noisy stage-1
outputs to clean GT midcurves. BCE, `adadelta`, nominally 500 epochs, batch 5.

Files: `denoiserencoderdecoder/build_denoiser_encoderdecoder_model.py`,
`main_denoiser_encoderdecoder.py`.

Issues:
- `build_denoiser_encoderdecoder_model.py:61`:
  `EarlyStopping(monitor='val_accuracy', mode='max', min_delta=1)` requires the
  validation accuracy to IMPROVE BY >= 1.0 (i.e. 100 percentage points) with default
  `patience=0`. Training therefore stops after ~2 epochs of the configured 500. The
  denoiser is effectively untrained. This alone explains poor denoiser results.
- Keras `adadelta` default lr (0.001) is far below the algorithm's intended 1.0;
  combined with the above, learning is negligible.
- No `restore_best_weights`, no checkpoint callback.
- The `__main__` block at `build_denoiser...py:80-90` feeds RAW 0-255 images into
  `simple_encoderdecoder.train` (violating the documented requirement that inputs be
  normalized to [0,1]); BCE on targets > 1 is mathematically invalid. The corrected
  path is `main_denoiser_encoderdecoder.py`; the stale `__main__` should not be used.
- Denoiser is trained and "tested" on stage-1 predictions of the same training set
  (`main_denoiser_encoderdecoder.py:25,33`): double leakage.

### 5. unet (documented best performer)

Architecture: 8-level encoder (kernel 5 then 4, stride 2, BN + LeakyReLU 0.2),
mirror decoder with dropout-0.5 skip concatenations, sigmoid heads; optional
auxiliary decoder reconstructs the input (loss weights [10, 1] midcurve vs aux).
Two stages: stage 1 = profile -> midcurve; stage 2 = (coords, profile, stage-1
midcurve) -> refined midcurve, aux reconstructs (profile, stage-1 midcurve).
Loss = custom weighted BCE via `tf.nn.weighted_cross_entropy_with_logits` after a
sigmoid->logit conversion (`unet/utils.py:24-50`), beta=0.1 (stage 1 unbalanced,
stage 2 balanced -> pos_weight 0.111). Data polarity: background=1, strokes=0, so
pos_weight < 1 correctly down-weights the abundant white background. CoordConv
channels in [-1,1]. Manual `train_on_batch` loop, Adam(decay=1e-4), no validation.

Files: `unet/unet.py`, `unet/train.py`, `unet/datagenerator.py`, `unet/utils.py`,
`unet/test.py`, `unet/run_stage2_only.py`, `unet/config.py`.

Issues:
- No validation or early stopping at all: weights are overwritten every epoch
  (`train.py:74-79`), and there is no signal for choosing an epoch count.
- `datagenerator.py:20-21` shuffles the file list ONCE; batch composition is
  identical every epoch (reduces the regularizing effect of SGD).
- `datagenerator.py:29-31`: wrap-around logic depends on `TRAIN_SIZE` imported from
  config (2100) while `train.py __main__` and `run_stage2_only.py` override
  `TRAIN_SIZE` only in the TRAIN module (320). If config `TRAIN_SIZE` ever exceeds
  the file count, `files[j]` raises IndexError. Fragile coupling.
- `train.py:28` `Adam(decay=0.0001)`: valid for the pinned keras 2.13, but removed
  in Keras 3 (would raise). Forward-compatibility risk given the repo already
  accommodates Keras 3 elsewhere.
- `utils.py:11-22` `get_coord_layers` uses `img_res[0]` for both axes; only correct
  for square images (currently always square). It is also recomputed per batch.
- Per-batch `print(_loss)` (`train.py:67,114`) floods stdout and slows training.
- prepare_data.py does NOT regenerate `unet-splits/` even though its docstring and
  CLAUDE.md say it does (`utils/prepare_data.py:8,48` define the path but no writer
  exists). The UNet dataset is a frozen artifact that cannot be rebuilt from raw data.

### 6. pix2pix (Keras GAN)

Architecture: standard Keras-GAN pix2pix; U-Net generator (7 down / 6 up + final
upsample), PatchGAN discriminator (16x16 patches, MSE/LSGAN loss), combined loss =
1 * LSGAN + 100 * MAE. Data: `keras_gan_data_loader.DataLoader` reads combo JPGs,
"binarizes" (values <= 192 -> 0), and normalizes to [-1, 1] (`/127.5 - 1`).

Files: `pix2pix/keras_gan_pix2pix.py`, `pix2pix/keras_gan_data_loader.py`,
`pix2pix/main_pix2pix.py`, `pix2pix/config.py`.

Issues:
- CRITICAL range mismatch: the generator's final activation is `sigmoid`
  (`keras_gan_pix2pix.py:112`, comment claims "matches the grayscale targets") but the
  DataLoader normalizes images to [-1, 1] (`keras_gan_data_loader.py:53-54,89-90`).
  Consequences: (a) the MAE target for stroke pixels is -1, unreachable from [0,1],
  so the best possible generator output for strokes is 0 (mid-gray after rescale);
  (b) the discriminator sees real B in [-1,1] and fake B in [0,1] and can separate
  them by value range alone, so the adversarial signal collapses;
  (c) `sample_images` rescales with `0.5*x+0.5`, mapping generated [0,1] to
  [0.5,1] - washed out. The model cannot learn the task correctly as written.
  Fix: `activation='tanh'`, or normalize data to [0,1] and drop the 0.5*x+0.5 rescale.
- `keras_gan_data_loader.py:96` `imageio.imread(path).astype(np.float)`: `np.float`
  was removed in numpy 1.24, and `environment.yml` pins `numpy=1.24.*`. Both
  `load_data` and `load_batch` crash on first call in the pinned environment.
- `keras_gan_data_loader.py:63` `for i in range(self.n_batches-1)`: drops the last
  batch every epoch; if the train dir holds fewer than 2*batch_size images the loader
  yields NOTHING and training silently does zero steps.
- `binarize` (`keras_gan_data_loader.py:15-21`) only forces values <= 192 to 0 and
  leaves 193-254 untouched (JPEG artifacts survive on the bright side), and it is an
  O(H*W) pure-Python double loop per image (very slow). Vectorized two-sided
  thresholding would be correct and ~1000x faster.
- `load_data` uses `np.random.choice(path, size=batch_size)` WITH replacement
  (`keras_gan_data_loader.py:26`): the 7-sample results grid can contain duplicates.
- `pix2pix/config.py:4` does `from config import *` after inserting `image_based/`
  into `sys.path`; when a script is run from inside `pix2pix/`, the name `config`
  resolves to this very file (already in `sys.modules`), so nothing is imported.
  Harmless today only because `keras_gan_pix2pix.py` uses no config symbols.

**Design-level caveat** (moved here from README.md's dead comment block, 2026-08-02, still
relevant after the 2026-08-02 bug fixes above): in a GAN, the discriminator's role is to learn
the cost function itself (what "looks right"), not to enforce an exact pixel-for-pixel match. For
MidcurveNN, each input profile has one exact correct midcurve output, so a plain L1/L2 loss (as
used by the plain encoder-decoders) is arguably a better-matched objective than an adversarial
one. The bug fixes above make pix2pix *runnable and structurally correct*, but don't resolve this
underlying question of whether a GAN is the right paradigm for an exact-output problem like this
one; worth comparing pix2pix's results against the plain encoder-decoders' once both are
evaluated on a leakage-free split (Rec 3).

### 7. img2img (PyTorch pix2pix)

Architecture: classic PyTorch pix2pix; 8-down/8-up U-Net generator with tanh output,
PatchGAN discriminator with sigmoid + BCE, L1 lambda = 100, Adam(2e-4, betas 0.5/0.999).
Data: combo JPGs via torchvision, resized to 256x512, normalized to [-1,1] (consistent
with tanh - correct, unlike the Keras variant), split into left/right halves.

Files: `img2img/main_img2img_pytorch.py`, `img2img/test_img2img.py`.

Issues:
- CRITICAL: `torchvision.datasets.ImageFolder(root=.../images-combo/train)`
  (`main_img2img_pytorch.py:41-49`) requires class subdirectories, but
  `images-combo/train` contains bare JPGs (verified: no subdirectories). ImageFolder
  raises "Couldn't find any class folder" at module import; the whole script is
  currently unrunnable. This is why `test_img2img.py` tests 02-04 are written to
  skip on import failure - they currently always skip. Fix: a small custom
  `Dataset` that lists *.jpg in the split directory.
- `main_img2img_pytorch.py:338` uses `sys.path.insert(...)` inside `main()`, but
  `import sys` is missing at the top of the module -> NameError AFTER training
  completes, so the results grid is never written.
- `weights_init` (`main_img2img_pytorch.py:180-187`) is defined but never applied to
  `Gen`/`Disc` (lines 194-195): the models train from PyTorch default init instead of
  the DCGAN N(0, 0.02) init the architecture was tuned for.
- `main_img2img_pytorch.py:281-284`: the progress print concatenates a format string
  with an already-formatted string, so the first half prints literal `{}` and the
  epoch/step/disc values are never shown. Logging only.
- Final evaluation uses only the first test batch (4 images) for a 7-column grid
  request (grid code caps n at 4 - cosmetic).
- `test_img2img.py:37-39` `_load_models` contains a broken line
  (`mod = importlib.util.load_from_spec = spec`) - unused helper, dead code.

### 8. testing/

`testing/test_image_based.py` covers data presence, model construction and forward
shapes for the four encoder-decoders + UNet import; sensible and consistent with the
CI constraints in CLAUDE.md. Per-approach `test_*.py` files duplicate this at approach
level and write JSON/text summaries. No functional bugs found beyond the dead
`_load_models` helper noted above. Note that no test would catch the pix2pix/img2img
runtime crashes because those tests intentionally skip on import failure.

### Shared pipeline notes (as they affect image_based)

- `utils/prepare_data.py:288-289` pairs profile/midcurve PNGs by sorting the two
  lists independently; correct today because names differ only in the
  Profile/Midcurve token, but it breaks silently (training on misaligned X/Y pairs)
  if any shape ever has an unpaired or extra file. Pairing by explicit filename
  substitution would be robust.
- `utils/prepare_data.py:317` rotations are 30..330 deg (docs say 0-350); raster
  rotation of already-rasterized 1-px strokes introduces interpolation blur and
  corner cropping. Rotating the point sequences BEFORE rasterizing (the code already
  has `rotate_sequence`) would produce clean augmented images.
- `utils/prepare_data.py:102-136` writes combo images as JPEG: lossy artifacts on
  binary line art force the downstream `binarize` hack. PNG would be lossless.
- `utils/prepare_plots.py:146-148` per-cell autoscale (`vmin=img.min(), vmax=img.max()`)
  makes an all-near-zero prediction look like a plausible curve in the results grid.
  Good for debugging, but it visually masks the class-imbalance failure mode; grids
  should also be rendered once with fixed [0,1] scale when judging quality.
- `utils/metric_utils.py:84-98` `print_best_metrics` raises KeyError if training ran
  zero epochs or `val_loss` never improved (empty `best_metrics`); edge case only.

---

## Bugs

Severity: High = wrong results or crash on the documented path; Medium = degrades
results or breaks a secondary path; Low = cosmetic/fragile.

1. ~~HIGH~~ FIXED (2026-08-02) - pix2pix generator/data range mismatch. Generator ended in
   `sigmoid` (`pix2pix/keras_gan_pix2pix.py:112`) while DataLoader normalizes to [-1,1]
   (`pix2pix/keras_gan_data_loader.py:53-54,89-90`). Stroke targets (-1) were
   unreachable; discriminator separated real/fake by value range; samples were
   rescaled wrongly. Fixed by changing the final activation to `tanh`, matching
   the DataLoader's [-1,1] normalization and the existing `0.5*x+0.5` display
   rescale in `sample_images` (which already assumed this range).

2. ~~HIGH~~ FIXED (2026-08-02) - pix2pix crash: `astype(np.float)`
   (`pix2pix/keras_gan_data_loader.py:96`). `np.float` was removed in numpy 1.24 and
   `src/environment.yml` pins `numpy=1.24.*`. Every data load crashed. Fixed by
   using the builtin `float` instead.

3. ~~HIGH~~ FIXED (2026-08-02) - img2img crash at import: `ImageFolder` pointed at flat
   directories `images-combo/train|test` which contain bare JPGs, no class subfolders
   (`img2img/main_img2img_pytorch.py:41-49`). Fixed by replacing `ImageFolder` with a
   small custom `ComboImageDataset` that lists `*.jpg` in the split directory directly.

4. ~~HIGH~~ FIXED (2026-08-02) - img2img `NameError: sys` in `main()`
   (`img2img/main_img2img_pytorch.py:338`); `import sys` was missing at top. Added.

25. ~~HIGH~~ FIXED (2026-08-02, found while verifying Bug 3's fix by actually running the
    test suite, not previously cataloged) - img2img `Gen`/`Disc` class-name shadowing:
    module-level code did `Gen = Gen(inst_norm).to(device)` and `Disc = Disc(inst_norm)
    .to(device)`, reassigning the class names to pre-built instances at import time. Any
    `from main_img2img_pytorch import Gen, Disc` (as `test_img2img.py` does) got an
    instance, not the class, so instantiating "fresh" models in tests
    (`Gen(inst_norm=False)`) actually called the instance's `forward()` with an invalid
    kwarg. This bug was invisible before because Bug 3 crashed the module at import
    before anyone could reach it. Fixed by renaming the instances to `generator`/
    `discriminator` throughout the file, leaving `Gen`/`Disc` as importable classes.

26. ~~MEDIUM~~ FIXED (2026-08-02, same discovery as Bug 25, not previously cataloged) -
    `test_pix2pix.py`'s `sys.path` setup added `src/` and `image_based/` but never
    `pix2pix/` itself, so `keras_gan_pix2pix.py`'s bare sibling imports (`from
    keras_gan_data_loader import DataLoader`, `from config import *`) raised
    `ModuleNotFoundError` when the test imported it as `pix2pix.keras_gan_pix2pix`.
    Fixed by adding `sys.path.insert(0, _HERE)` in the test file.

5. ~~HIGH~~ FIXED (2026-08-02) - denoiser effectively untrained:
   `EarlyStopping(monitor='val_accuracy', mode='max', min_delta=1)` with default
   patience=0 (`denoiserencoderdecoder/build_denoiser_encoderdecoder_model.py:61`)
   stopped training after ~2 of 500 epochs because accuracy could never improve by
   1.0. Fixed: `EarlyStopping(monitor='val_loss', mode='min', patience=20,
   restore_best_weights=True)`, optimizer changed from default `adadelta` (lr=0.001,
   far below the algorithm's intended 1.0) to `Adam(1e-3)`, per Rec 4. Construction/
   shape-level tests pass; a full 500-epoch training run was not executed this
   session (impractical to smoke-test).

6. ~~HIGH~~ FIXED (2026-08-02) - evaluation on training data: all four encoder-decoder
   mains drew their "test" images from the training arrays
   (`simpleencoderdecoder/main_simple_encoderdecoder.py:21`,
   `cnnencoderdecoder/main_cnn_encoderdecoder.py:25`,
   `denseencoderdecoder/main_dense_encoderdecoder.py:22`,
   `denoiserencoderdecoder/main_denoiser_encoderdecoder.py:33`). Fixed in all four by
   excluding the sampled test indices from the training arrays before training (for
   the two-stage denoiser, applied to both stage-1 and stage-2 training). Note: this
   fixes literal train/test overlap, not the separate augmentation-level leakage
   (Bug 7) where a held-out sample can still be a rotated/translated variant of a
   shape seen during training. `simpleencoderdecoder` verified via a full real
   training run (100 epochs, ~66s, predicted cleanly on the now-genuinely-unseen 7
   test samples); `denseencoderdecoder` verified partially (25/100 epochs, no errors,
   stopped only for session time budget -- identical fix pattern to simple); `cnn`/
   `denoiser` verified via passing construction/shape tests plus code review (full
   runs not executed: cnn's own comment estimates ~23 min, denoiser trains two
   models).

7. MEDIUM - augmentation-level leakage in all splits: `generate_pix2pix_dataset`
   shuffles augmented variants before splitting (`utils/prepare_data.py:102-108`),
   and unet-splits was built the same way, so val/test are rotations/translations of
   training shapes. No held-out-shape evaluation exists anywhere in Phase I.

8. ~~MEDIUM~~ FIXED (2026-08-02) - dense model saves last-epoch weights: EarlyStopping
   without `restore_best_weights` and no ModelCheckpoint
   (`denseencoderdecoder/build_dense_encoderdecoder_model.py:76,89`); saved model could
   be up to 50 epochs past the best validation loss. Fixed by adding
   `restore_best_weights=True`.

9. ~~MEDIUM~~ FIXED (2026-08-02) - CNN callbacks monitor train loss (`monitor='loss'`)
   despite a validation split (`cnnencoderdecoder/build_cnn_encoderdecoder_model.py:
   107-108`); best-weight restoration tracked overfitting, not generalization. Fixed:
   both `EarlyStopping` and `ReduceLROnPlateau` now monitor `val_loss`.

10. ~~MEDIUM~~ FIXED (2026-08-02) - pix2pix `load_batch` off-by-one: `range(self.n_batches-1)`
    (`pix2pix/keras_gan_data_loader.py:63`) dropped one batch per epoch and yielded
    nothing at all when the folder had fewer than 2*batch_size images. Fixed to
    `range(self.n_batches)`.

11. MEDIUM - `utils/prepare_data.py` never writes `unet-splits/` although its
    docstring (line 8) and CLAUDE.md claim it does; `UNET_SPLITS_DIR` (line 48) is
    unused. The UNet train/test set (2100/900 PNGs) cannot be regenerated from raw
    data; changing raw data or augmentation cannot propagate to UNet.

12. ~~MEDIUM~~ FIXED (2026-08-02) - denoiser stale `__main__`
    (`denoiserencoderdecoder/build_denoiser_encoderdecoder_model.py:80-90`) trained
    the stage-1 model on raw 0-255 arrays (invalid BCE targets > 1), contradicting
    the documented requirement to normalize first. Confirmed `main_denoiser_
    encoderdecoder.py` already does this correctly (`/255.` before training); deleted
    the stale duplicate `__main__` block and its now-unused imports
    (`simple_encoderdecoder`, `get_training_data`, `plot_results`, `random`).

13. ~~MEDIUM~~ FIXED (2026-08-02) - img2img `weights_init` never applied
    (`img2img/main_img2img_pytorch.py:180-195`); DCGAN init is defined but models use
    default init. Fixed: `generator.apply(weights_init)` /
    `discriminator.apply(weights_init)` added right after instantiation.

14. ~~MEDIUM~~ FIXED (2026-08-02) - CNN build-file `__main__` NameError: used
    `get_training_data`/`plot_results` without importing them
    (`cnnencoderdecoder/build_cnn_encoderdecoder_model.py:136,147`); also passed
    `100` as the boolean `retrain_model` argument (line 139). Fixed by deleting the
    whole stale, superseded `__main__` block (same treatment as Bug 12/denoiser and
    the newly-found equivalent blocks in `simpleencoderdecoder`/`denseencoderdecoder`
    -- all four build files had a redundant, leaky debug entry point duplicating what
    their real `main_*.py` files already do correctly).

15. ~~LOW~~ FIXED (2026-08-02) - pix2pix `binarize` only thresholded the dark side
    (values 193-254 kept) and used a per-pixel Python loop
    (`pix2pix/keras_gan_data_loader.py:15-21`). Fixed: vectorized two-sided
    `np.where(image <= threshold, 0, 255)`.

16. ~~LOW~~ FIXED (2026-08-02) - pix2pix `load_data` sampled test images WITH
    replacement (`pix2pix/keras_gan_data_loader.py:26`); results grid could show
    duplicates. Fixed: `replace=False`, capped at `len(path)` to avoid an error when
    `batch_size` exceeds the split size.

17. ~~LOW~~ FIXED (2026-08-02) - `pix2pix/config.py:4` self-import: running scripts
    from inside `pix2pix/` resolved `config` to this file itself, importing nothing
    (harmless only because nothing read a config symbol). Root cause: it only walked
    up 2 directories (to `image_based/`, which has no `config.py`) instead of 3 (to
    `src/`), using the self-import-prone `from config import *` pattern instead of
    `unet/config.py`'s safer `importlib`-based re-export. Fixed by mirroring
    `unet/config.py`'s exact pattern (load `src/config.py` under a unique
    `sys.modules` name, then populate this module's globals from it).

18. ~~LOW~~ FIXED (2026-08-02) - UNet `Adam(decay=0.0001)` (`unet/train.py:28,58,101`):
    fine on pinned keras 2.13, raises on Keras 3 (rest of repo is already Keras-3
    hardened). Fixed with a `_make_adam()` helper using
    `InverseTimeDecay(decay_steps=1, decay_rate=0.0001)`, which reproduces the exact
    same per-iteration decay schedule (`lr_t = lr_0 / (1 + decay*step)`) via a
    non-deprecated API. Verified via `pytest image_based/unet/test_unet.py` (12/12
    passed, up from 9/12 -- see Bugs 27, 28 below, found while investigating the
    other 3 failures during this verification).

27. ~~LOW~~ FIXED (2026-08-02, new, found while verifying Bug 18) -
    `unet/test_unet.py` import ordering: its own module-level `sys.path.insert(0,
    _SRC)` then `sys.path.insert(0, _HERE)` put `_SRC` (src/) ahead of `_HERE`
    (unet/) despite the comment's stated intent; separately, `setUpClass`'s `from
    unet import unet_stage1, unet_stage2` transitively imports `unet/config.py`,
    which inserts `src/` onto `sys.path` *again*, re-pushing it above `unet/`. Net
    effect: `from utils import get_coord_layers` (etc.) in `TestUNetModel` found
    `src/utils/` (the package) instead of `unet/utils.py`, a `unet/test.py`-style
    import-ordering bug (see the documented gotcha in `CLAUDE.md`) that had gone
    unnoticed because these 3 tests were never run to completion before. Fixed by
    re-asserting `unet/`'s `sys.path` priority and evicting the cached `utils`
    module immediately before each affected test's import, mirroring `unet/test.py`'s
    established fix pattern.

28. ~~LOW~~ FIXED (2026-08-02, new, found while verifying Bug 18/27) -
    `unet/test_unet.py::test_09_coordconv_importable` asserted `from utils import
    get_coord_layers, CoordConv`, but `unet/utils.py` has never defined a `CoordConv`
    symbol -- `get_coord_layers()` itself is the CoordConv implementation (generates
    the coordinate channels to concatenate). The test was asserting an import that
    never existed in the source, just silently masked by Bug 27's import-ordering
    issue (which made the test fail with a *different*, misleading error first).
    Fixed by correcting the test to import only `get_coord_layers`.

19. ~~LOW~~ FIXED (2026-08-02) - `unet/datagenerator.py:29-31` wrap logic used config
    `TRAIN_SIZE` (2100) while train entry points override `TRAIN_SIZE` only in the
    train module (320); IndexError if config TRAIN_SIZE ever exceeded the file count;
    file order was shuffled once, never per epoch. Fixed: uses the real `len(files)`
    as the wrap-around bound (decoupled from config entirely) and reshuffles at the
    start of every epoch, not just once at generator creation.

20. ~~LOW~~ FIXED (2026-08-02) - img2img progress print formats only half the message
    (`img2img/main_img2img_pytorch.py:281-284`); epoch/loss values never shown. Fixed by
    parenthesizing the concatenated string before calling `.format()` on it.

21. ~~LOW~~ FIXED (2026-08-02) - `unet/utils.py:14-16` `get_coord_layers` used
    `img_res[0]` for both axes (breaks for non-square inputs) and was rebuilt every
    batch. Fixed: separate x/y ranges and normalization for `(h, w)`, plus an
    `lru_cache`-backed `_base_coord_layer(h, w)` helper so the per-pixel coordinate
    grid is computed once per resolution instead of on every batch. Verified correct
    for a non-square case: `get_coord_layers(2, (100, 60))` -> shape `(2, 100, 60, 2)`,
    both channels correctly normalized to [-1, 1].

22. ~~LOW~~ FIXED (2026-08-02) - `img2img/test_img2img.py:37-39` broken, unused
    `_load_models` helper (`mod = importlib.util.load_from_spec = spec`). Deleted (dead
    code, never called by any test).

23. ~~LOW~~ FIXED (2026-08-02) - `utils/metric_utils.py:92-98` KeyError on empty
    `best_metrics` if no epoch ever produced a `val_loss` improvement. Fixed with an
    early-return guard that prints a graceful message instead of crashing.

24. ~~LOW~~ FIXED (2026-08-02) - pairing by independent sorts in
    `utils/prepare_data.py:288-289` silently misaligned X/Y pairs if a shape ever had
    an unpaired Profile/Midcurve file. Fixed: pairs explicitly by deriving each
    profile's expected midcurve filename via substitution and only keeping pairs
    where both files exist (warns and skips orphans), instead of trusting two
    independently-sorted lists to stay aligned. Verified via
    `pytest image_based/testing/test_image_based.py::TestPrepareData` (both tests
    pass, including a fresh-run of `test_read_dat_files`).

---

## Accuracy Improvement Recommendations

Ordered by expected impact.

1. Fix the class-imbalance loss for simple/cnn/dense/denoiser (highest impact).
   Reuse `unet/utils.py:weighted_cross_entropy` (it is generic) or add a Dice /
   soft-IoU / focal loss. With ~0.2-1% positive pixels, plain BCE converges to
   near-blank outputs. A combined loss (WBCE + Dice) is the standard fix for thin
   structures. Expected effect: the faint low-contrast predictions become crisp
   curves; this is the difference between "visible only via autoscale" and usable.

2. Fix the pix2pix output range (Bug 1): change `activation='sigmoid'` to `'tanh'`
   in `keras_gan_pix2pix.py:112` (and keep the 0.5*x+0.5 display rescale), or
   normalize the DataLoader to [0,1]. Also fix Bugs 2 and 10 so the loader runs and
   uses all batches. Until then pix2pix results are structurally invalid.

3. Introduce a leakage-free evaluation protocol (Bugs 6, 7): split by BASE SHAPE
   (all augmented variants of a shape stay on one side), regenerate images-combo and
   an image-pairs split accordingly, and make every main script load its grid samples
   from the held-out split. Without this, no accuracy claim for Phase I is reliable,
   and improvements cannot be measured.

4. Repair the denoiser training schedule (Bug 5): `EarlyStopping(monitor='val_loss',
   mode='min', patience=20, restore_best_weights=True)`, optimizer `Adam(1e-3)`
   instead of default adadelta, and train stage 2 on stage-1 predictions of a split
   disjoint from the denoiser's own validation. The two-stage idea mirrors UNet's
   refinement and should work once it actually trains.

5. Add quantitative, skeleton-aware metrics for all image approaches: Dice/IoU at a
   fixed threshold, plus Chamfer and Hausdorff distances between thresholded predicted
   pixels and GT midcurve pixels (a tolerance-based "correct within r px" measure
   is standard for centerline extraction). This also enables an apples-to-apples
   comparison with Phase II/III numbers (MAE/Hausdorff already reported there) and
   with `src/benchmark.py`.

6. Soften/thicken the target: dilate GT midcurves by 1-2 px (or convolve with a small
   Gaussian) before training, or regress the distance transform instead of a binary
   mask. Thin 1-px targets make the loss landscape needle-like; a 3-px target with a
   post-hoc skeletonization recovers the 1-px answer while training far more stably.

7. Post-processing for clean polylines: threshold (choose the threshold by maximizing
   Dice on validation instead of a fixed 0.5) -> morphological closing ->
   `skimage.morphology.skeletonize` -> vectorize. This directly addresses the Phase I
   limitation noted in the research context and improves every reported geometric
   metric at zero training cost.

8. Better augmentation in `utils/prepare_data.py`: rotate/mirror/translate the POINT
   SEQUENCES (functions already exist: `rotate_sequence`, `mirror_sequence`,
   `translate_sequence`) and rasterize each variant, instead of transforming rasters
   (which blurs and crops strokes). Add scale augmentation (rasters currently encode
   absolute size). Save combos as PNG, not JPEG. Regenerate unet-splits from the same
   pipeline (fixes Bug 11).

9. UNet training loop hygiene: hold out a validation subset, track validation WBCE +
   Dice per epoch, keep the best checkpoint instead of overwriting every epoch,
   reshuffle the file list each epoch in `datagenerator.py`, and replace per-batch
   `print` with an epoch-level average. Consider a cosine or step LR schedule; the
   fixed Adam with tiny decay over an unvalidated epoch count makes results depend on
   the arbitrary final epoch.

10. CNN/simple/dense capacity and callbacks: monitor `val_loss` everywhere
    (Bugs 8, 9), add `restore_best_weights=True` + ModelCheckpoint to dense; for CNN
    use bilinear interpolation when resizing to 128, or regenerate 128x128 rasters
    natively; for simple, the 100-dim bottleneck is the binding constraint - either
    accept it as a baseline or raise it to 512+.

11. img2img: after fixing Bugs 3/4, apply `weights_init` to both nets
    (`Gen.apply(weights_init); Disc.apply(weights_init)`), train for more than 5
    epochs with an L1-vs-GAN loss curve check, and evaluate on more than one test
    batch. Consider dropping the redundant RGB conversion (grayscale, dim_c=1) for a
    3x cheaper model on this line-art data.

12. Threshold-aware reporting: render results grids BOTH with per-cell autoscale
    (debugging) and with fixed vmin=0, vmax=1 (honest quality view), via a flag on
    `save_results_grid_images`.

---

## Summary Table

| Approach | Loss / activation | Data | Trains OK? | Main problems | Priority fixes |
|---|---|---|---|---|---|
| simpleencoderdecoder | BCE / sigmoid | image-pairs 100x100 (fg under 1%) | Yes (Bug 6 fixed 2026-08-02, verified via full real training run) | class imbalance; was: eval on train set | Rec 1, 3 (done) |
| cnnencoderdecoder | BCE / sigmoid | image-pairs upscaled to 128 | Yes (Bugs 6, 9, 14 fixed 2026-08-02, construction tests pass, full run not executed) | class imbalance; nearest resize; was: eval on train set; callbacks on train loss; broken __main__ | Rec 1, 3 (done), 10 (done) |
| denseencoderdecoder | BCE / sigmoid | image-pairs 100x100 | Yes (Bugs 6, 8 fixed 2026-08-02, verified via partial real training run) | class imbalance; was: eval on train set; saved last-epoch weights | Rec 1, 3 (done), 10 (done) |
| denoiserencoderdecoder | BCE / sigmoid | stage-1 outputs | Should now (Bugs 5, 6, 12 fixed 2026-08-02; construction-level tests pass, full training run not executed) | class imbalance; was: broken EarlyStopping; adadelta lr; eval on train set (both stages) | Rec 4 (done), 1 |
| unet | WBCE beta=0.1 / sigmoid | unet-splits 256x256 | Yes (Bug 18 fixed 2026-08-02, verified via `pytest ... test_unet.py`, 12/12) | no validation/best-checkpoint; dataset not regenerable (Bug 11); was: Keras-3-incompatible optimizer | Rec 9, 8, 5 |
| pix2pix (Keras) | LSGAN + 100*MAE / tanh (fixed 2026-08-02) | images-combo [-1,1] | Yes (Bugs 1, 2, 10, 15, 16, 17, 26 fixed 2026-08-02, verified via real pytest run) | was: output-range mismatch; np.float crash; batch drop; one-sided binarize; sampling w/ replacement; config self-import | Rec 2 (done) |
| img2img (PyTorch) | BCE-GAN + 100*L1 / tanh (correct) | images-combo [-1,1] | Yes (Bugs 3, 4, 13, 20, 25 fixed 2026-08-02, verified via real pytest run) | was: ImageFolder crash; missing import sys; init unused; Gen/Disc shadowing | Rec 11 (done) |

Overall: the UNet is the only approach whose loss matches the data statistics, which
is consistent with it being the documented Phase I best. The fastest route to better
Phase I accuracy is (1) weighted/Dice losses for the four plain encoder-decoders,
(2) making pix2pix and img2img runnable and range-consistent, (3) a leakage-free
shape-level split so improvements are actually measurable, and (4) skeletonization
post-processing plus geometry-aware metrics for honest comparison with Phase II/III.
