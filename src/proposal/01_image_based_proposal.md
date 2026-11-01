## Phase I (image-based) review and upgrade proposal

Scope: `src/image_based/*`, `src/config.py`, `src/utils/prepare_data.py`, `src/utils/prepare_plots.py`,
`src/utils/metric_utils.py`, `src/image_based/analysis_report.md`, `TODO.md`. Static analysis only: no
training run, no data regeneration, no git. Result grids were inspected as images
(`*/results/results_grid.png`).

## 1. Summary (read this first)

1. The poor results are mostly NOT a "wrong architecture" problem. They come from five things that are
   cheap to fix: (a) a loss that rewards blank output, (b) far too few optimiser steps for the CNN, UNet
   and GAN runs, (c) input representation (a 1-px outline only, no filled mask / distance cue), (d)
   evaluation that is either leaked (random split over augmented poses) or purely visual, and (e) models
   that can shortcut (additive full-resolution skip in the CNN; no real bottleneck).
2. "Simple" and "dense" look OK only because they are interpolating: 448 images are 4 shapes x
   112 poses, and the test sample is a different pose of a shape seen in training
   (`main_simple_encoderdecoder.py:22-26`). They cannot generalise to new shapes or poses by design (a
   fully connected net has no translation/rotation structure).
3. The documented "best" UNet is, in the committed grid (`unet/results/results_grid.png`), collapsed: all 7
   different inputs give the same faint blob. The only recorded run is 5 epochs x 20 batches = 100 steps
   (`unet/train.py:156-157`) with a loss that still weights background about 50x more than ink (Section 2.5).
   So there is no valid evidence that UNet is "best".
4. The UNet data (`unet-splits`, 3000 images from random T/I/L/E/C/F drawn by `utils/create_ds.py`) is a
   different dataset from the 448 `image-pairs`, so UNet and the other models were never compared on the
   same data.
5. Proposal: one new PyTorch package `src/image_based/midcurve_img/` with ONE driver
   (`python -m image_based.midcurve_img.train --arch unet ...`), an on-the-fly rasteriser that reads the
   existing `text_based/data/brep/*.json` (no `drawsvg`, no regenerated files, no new tracked data),
   leave-one-shape-out evaluation, tolerance metrics (F1 within 2 px, Chamfer, Hausdorff, topology counts),
   and a skeletonise post-process. Legacy Keras folders are frozen, not deleted.
6. Honest limit: with only I, L, T, Plus, "held-out shape" accuracy is a weak test (holding out Plus
   removes the only 4-way junction). Generalisation claims need more shape families (Section 5.6).

## 2. Diagnosis per model (why results are poor)

Data facts (verified): `image-pairs/` has 896 PNGs = 448 pairs = 4 shapes (I, L, Plus, T) x 112 poses
(mirror x rotate x translate), 100x100 RGBA, ink in alpha. Profile is an OUTLINE (`prepare_data.py:367`,
`fill='none'`), midcurve a 1-px open polyline. Ink is well under 1 percent of pixels. Committed
`images-combo/` is 268/89/91 (flat shuffle, the shape-grouped split code at `prepare_data.py:65-109,164`
exists but was never run on the committed data). Committed `unet-splits/` is 2100/900 of the other dataset.

### 2.1 simpleencoderdecoder (`simpleencoderdecoder/build_simple_encoderdecoder_model.py`)
- :35-40 Dense(100) code with L1 activity regulariser, BatchNorm and Dropout(0.2) ON THE CODE. Dropout on a
  100-d bottleneck throws away 20 percent of the entire representation; BN on a code with batch 16 is noisy.
- :54-55 plain `binary_crossentropy`; positives well under 1 percent, so blank-ish output is near optimal.
  Visible in the grid as faint ghost lines with the real line only partly sharp.
- `main_simple_encoderdecoder.py:22-26,33` test = random poses of training shapes (interpolation).
- Why it still "works": a 100-d code is enough to memorise 4 shapes x pose manifold, and the output layer
  is an unconstrained 100 -> 10000 linear map (a lookup).

### 2.2 denseencoderdecoder (`denseencoderdecoder/build_dense_encoderdecoder_model.py`)
- :32-37 10000-2048-1024-100-1024-2048-10000, ELU, no normalisation, ~45M weights for 313 train images.
- :50-52 lr 1e-4 with BCE; :82 `validation_split=0.3` (random poses, so val_loss is optimistic and early
  stopping picks nothing meaningful).
- Hallucinated stray segments in the grid (extra tick marks at junctions) are the lookup-table failure.
- Cannot ever generalise to unseen poses of a new shape (no shift/rotation structure).

### 2.3 cnnencoderdecoder (`cnnencoderdecoder/build_cnn_encoderdecoder_model.py`, `main_cnn_encoderdecoder.py`)
Grid shows a faint copy of the INPUT OUTLINE (ghost T, L, plus) and almost no midcurve. Causes, in order:
1. :36-38,75 `skip1` is the output of ONE conv on the raw input at full resolution and is ADDED back at the
   last decoder level. The easiest solution for the net is to copy the outline. Additive skips of shallow
   features into a task whose output is semantically different from the input (outline vs centreline)
   invite this shortcut.
2. :55-58 the deepest level is 16x16x256 = 65,536 values for a 128x128 = 16,384 pixel image: there is no
   bottleneck at all, so nothing forces abstraction either.
3. :85 BCE with ~0.2 percent positives. Ghost-copy of the outline (a few percent of mass) beats blank.
4. `main_cnn_encoderdecoder.py:81` `epochs = 15`, batch 16, 313 train images -> about 20 steps per epoch,
   about 300 optimiser steps in total. A conv net on thin lines needs thousands. The code comment says
   "quick run: ~23 min" so this was never a converged run. Plus :106 EarlyStopping patience 10 and
   ReduceLROnPlateau could stop it even earlier.
5. `prepare_data.py:293` `load_img(..., target_size=(128,128))` resizes 100 -> 128 with default
   nearest-neighbour: 1-px strokes become irregular 1-2 px staircases that differ between input and target.
6. :39,43,... BatchNorm after every conv with `activation='relu'` inside the conv (BN after ReLU): works but
   stats are computed on a mostly-empty image; with GN/IN it would be batch independent.
7. `main_cnn_encoderdecoder.py:52-58` CoordConv channels are fine but normalised /127 (not centred); minor.

### 2.4 denoiserencoderdecoder (`denoiserencoderdecoder/*`)
- `main_denoiser_encoderdecoder.py:36-43`: stage 1 is trained on the training set, then asked to predict the
  SAME training set; those predictions are near-clean, so the denoiser trains on "almost clean -> clean" and
  learns the identity. At test time it receives genuinely noisy stage-1 output it never saw (distribution
  shift). A denoiser needs synthetic corruption or out-of-fold stage-1 predictions.
- `build_denoiser_encoderdecoder_model.py:33-42` two 2x2 pools, no skips, BCE, input is ONLY the noisy
  midcurve (no profile), so it cannot fix a wrong line, only smooth it.
- :20-21 batch 5; BCE again.

### 2.5 unet (`unet/*`)
- `unet.py:29-44`: eight stride-2 levels take 256 -> 1x1 (512 channels at 1x1). Receptive field is the whole
  image but the bottleneck is a single vector; with kernel 5/4 and filters 64..512 this is tens of millions
  of parameters for a 4-shape problem.
- `utils.py:56-60`: weighted BCE with `pos_weight = beta = 0.1` (stage 1, `config.py:20-21`, balanced False)
  on data where ink = 0 and background = 1 (`datagenerator.py:49-50`, white background). So the label-1
  class (background, about 99.8 percent) gets weight 0.1 and ink gets weight 1: net ratio about 10:1 in
  favour of ink, against an actual pixel ratio of about 500:1. Ink mass is still about 2 percent of the loss
  versus 98 percent for background. Stage 2 `balanced=True` gives `0.1/0.9 = 0.111`, the same story.
  (The analysis report says this "matches the data statistics"; it only moves the weighting 10x of the 500x
  needed.)
- `train.py:156-157` `epochs = 5`, `TRAIN_SIZE = 320`, batch 16 -> 100 optimiser steps for stage 1 and 100
  for stage 2. The committed result grid (identical blob for all 7 inputs) is exactly the "collapsed
  untrained" signature. `training_run.log` ends in a Keras 3 `.weights.h5` filename crash.
- `unet.py:69-81` `Dropout(0.5)` on every decoder level (pix2pix habit for noise); with 100 steps it only
  slows learning. `train.py:45` aux decoder reconstructing the input with weight 1 vs 10 adds nothing.
- `train.py:123` stage 2 calls `generator_stage1.predict` per batch (slow, also uses stage-1 output on its
  own training data, same leakage as the denoiser).
- No validation, no best-checkpoint, no metric: `unet/test.py` only draws images.
- Data: the legacy 3000-image set (T/I/L/E/C/F, random sizes, `utils/create_ds.py`) is richer than the 448
  pairs, but file names carry no shape id (`C123.png`), so it can only support pose-level (interpolation)
  splits, and it is not regenerable (`analysis_report.md` Bug 11).

### 2.6 pix2pix, Keras (`pix2pix/keras_gan_pix2pix.py`, `keras_gan_data_loader.py`, `main_pix2pix.py`)
- `keras_gan_pix2pix.py:65-67` loss `[mse, mae]` weights `[1, 100]`: MAE between a generated image and a
  target that is 99.8 percent white. All-white output is a very strong attractor and 100x L1 swamps the
  adversarial term.
- `main_pix2pix.py:15` `epochs=5`, `batch_size=1` -> 5 x 268 = 1340 steps. Pix2pix papers use tens to
  hundreds of thousands of steps.
- :77,86,124 `BatchNormalization(momentum=0.8)` with batch size 1: batch statistics of a single image
  (CLAUDE.md already warns about BN and batch 1). Use InstanceNorm/GroupNorm or batch >= 8.
- :156 `generator.predict` inside the train loop each step (slow, retraces); D and G are separate
  `train_on_batch` calls with `valid`/`fake` patch targets, fine.
- Loader: JPEG line art (`prepare_data.py:193`) binarised with a threshold; images came from 100 px
  nearest-upscaled to 256 (`prepare_data.py:150`), so strokes are 2.56 px blocks. Test split is flat random
  over poses (leak). Only `fliplr` augmentation; no rotation, so the model sees a fixed 224 poses.
- 7 down-sampling stages to 2x2 (:93-100) plus dropout-free BN; heavy for the data.

### 2.7 img2img, PyTorch (`img2img/main_img2img_pytorch.py`)
- :266 `L1_lambda = 100.0` unweighted L1 on near-white images (same blank attractor); :265 `epochs = 5`,
  :36 `batch_size = 4` -> 67 steps per epoch, about 335 steps in total.
- :163-165 `F.dropout(..., training=True)` is hard-wired ON, also at inference; `generator.eval()` (:316,357)
  does not turn it off, so test outputs are random per call.
- :92,107,122 BatchNorm unless `batch_size == 1`, and then InstanceNorm. Batch 4 BN on sparse images is
  weak; GroupNorm/InstanceNorm always.
- :127 `dim_c = 3`: JPEG converted to RGB, 3x compute for greyscale line art, JPEG noise included
  (:57 `.convert('RGB')`, no binarise).
- :39-41 `Resize((256,512))` of already 256x512 images is a no-op but uses default bilinear if sizes differ.
- :210-222 constant lr 2e-4, no scheduler, no validation, no metric, and NO `torch.save` anywhere
  (verified: no checkpoint is ever written, a trained model is lost when the process exits).
- :274-275 patch masks hard-coded 30x30 (correct only for 256 px input).
- `torchvision` is not installed in the `genai` env (see `img2img/results/test_results.txt`), so
  `test_img2img.py` tests 02-04 always skip. New code must not import torchvision.

### 2.8 Cross-cutting root causes (ranked by expected impact)
1. Loss / class imbalance (all models).
2. Too few optimiser steps (CNN ~300, UNet 100+100, pix2pix 1340, img2img ~335). Fix with on-the-fly
   augmentation (infinite data) and 5-20k steps.
3. Input representation: outline only. Midcurve is (for these shapes) the medial axis of the FILLED polygon.
   Giving the net a filled mask and a distance transform channel turns "find the middle between two thin
   outlines" into "find the ridge of a smooth field". This is the single biggest trick.
4. Evaluation: random split over poses (leak), "test" is looking at 7 pictures, per-cell autoscaled grids
   (`prepare_plots.py:146-148`) hide faint predictions, accuracy metric is meaningless (99 percent for blank).
5. Architecture shortcuts: additive full-res skip (CNN), no skip at all (simple/dense/denoiser), 1x1
   bottleneck and dropout everywhere (UNet), BN with batch 1 (Keras pix2pix).
6. Data scale: 4 shapes. Even a perfect model only demonstrates pose interpolation.
7. Resolution/aliasing: nearest-neighbour resize of 1-px strokes; JPEG for line art.

## 3. Prioritised tweaks with PyTorch code

Order = expected gain per hour. T1-T6 are essential; T7-T12 are polish. All code below is the reference
implementation that Section 6 asks Sonnet to place into files under `src/image_based/midcurve_img/`.
Conventions: ink = 1.0 and background = 0.0 INSIDE the new code (legacy files store the opposite; convert
at the boundary only). Models output LOGITS (no sigmoid), losses use `*_with_logits`. No torchvision.

### T1. Loss: soft target + pos-weighted BCE + Dice (file `losses.py`)
Blur the 1-px target slightly (sigma about 1.2 px) so a near miss still gets gradient; weight positives
about 10x (not 500x; blurring already widens the positive mass); add soft Dice, which is scale free and
ignores the background count entirely.

```python
# losses.py
import torch
import torch.nn.functional as F


def _gauss1d(sigma, device, dtype):
    r = max(1, int(3 * sigma))
    x = torch.arange(-r, r + 1, device=device, dtype=dtype)
    k = torch.exp(-(x ** 2) / (2 * sigma ** 2))
    return k / k.sum()


def blur(t, sigma=1.2):
    """Separable Gaussian blur of a (B,1,H,W) tensor."""
    k = _gauss1d(sigma, t.device, t.dtype)
    r = k.numel() // 2
    t = F.conv2d(F.pad(t, (r, r, 0, 0), mode="replicate"), k.view(1, 1, 1, -1))
    t = F.conv2d(F.pad(t, (0, 0, r, r), mode="replicate"), k.view(1, 1, -1, 1))
    return t


def soft_target(y_thin, sigma=1.2):
    s = blur(y_thin, sigma)
    return s / s.amax(dim=(2, 3), keepdim=True).clamp_min(1e-6)


def dice_loss(logits, target, eps=1.0):
    p = torch.sigmoid(logits)
    inter = (p * target).sum(dim=(1, 2, 3))
    den = p.sum(dim=(1, 2, 3)) + target.sum(dim=(1, 2, 3))
    return (1.0 - (2 * inter + eps) / (den + eps)).mean()


def focal_bce(logits, target, gamma=2.0, alpha=0.75):
    bce = F.binary_cross_entropy_with_logits(logits, target, reduction="none")
    p = torch.sigmoid(logits)
    pt = target * p + (1 - target) * (1 - p)
    a = target * alpha + (1 - target) * (1 - alpha)
    return (a * (1 - pt) ** gamma * bce).mean()


def seg_loss(logits, y_thin, pos_weight=10.0, sigma=1.2, dice_w=1.0, kind="bcedice"):
    t = soft_target(y_thin, sigma)
    if kind == "focaldice":
        return focal_bce(logits, t) * 10.0 + dice_w * dice_loss(logits, t)
    pw = torch.tensor(float(pos_weight), device=logits.device)
    bce = F.binary_cross_entropy_with_logits(logits, t, pos_weight=pw)
    return bce + dice_w * dice_loss(logits, t)
```
Optional (T1b): distance-weighted BCE, weight = `1 + 10*exp(-d/3)` with `d` = distance to nearest GT
pixel (from `scipy.ndimage.distance_transform_edt(1 - y)` in the dataset); gives hard negatives next to the
line more weight than empty corners. Optional (T1c): clDice or a Chamfer surrogate. Not needed first.

Also initialise the last conv bias to -4 (about 2 percent prior), which removes the initial huge loss and
the "predict nothing first" phase (done in `UNetLite` below).

### T2. Richer input: outline + FILLED mask + distance transform (file `data.py`)
Channels: 0 = outline (1 px), 1 = filled polygon, 2 = distance transform of the filled polygon divided by
its max (so scale free). The midcurve is the ridge of channel 2. Even `skimage.morphology.skeletonize` of
channel 1 gives a decent baseline (Section 3 T11), which the net must beat. Costs nothing. Also gives
dense/simple/denoiser a fair chance.

### T3. On-the-fly augmentation = effectively infinite data (file `data.py`)
Render from the polygon with random rotation (0-360), mirror, scale (35-80 percent of the frame) and
translation, applied identically to profile and midcurve coordinates BEFORE rasterising (no raster
rotate/crop blur, no nearest-neighbour resize). 100-200 steps x batch 16 per "epoch" of fresh samples; 60
epochs = 6-12k steps. Complete reference implementation:

```python
# data.py
import json, math, os
import numpy as np
import cv2
import torch
from scipy import ndimage as ndi
from torch.utils.data import Dataset

SRC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BREP_DIR = os.path.join(SRC, "text_based", "data", "brep")


def load_shapes(brep_dir=BREP_DIR):
    """name -> dict(profile Nx2, mpts Mx2, mlines Kx2). Branched midcurves use the brep 'Lines'."""
    shapes = {}
    for fn in sorted(os.listdir(brep_dir)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(brep_dir, fn)) as f:
            d = json.load(f)
        mb = d["Midcurve_brep"]
        shapes[d["ShapeName"]] = dict(
            profile=np.asarray(d["Profile"], np.float32),
            mpts=np.asarray(mb["Points"], np.float32),
            mlines=np.asarray(mb["Lines"], np.int64))
    return shapes


def _pose(rng, size, ext, aug):
    if aug:
        theta = rng.uniform(0, 2 * math.pi)
        mirror = bool(rng.random() < 0.5)
        frac = rng.uniform(0.35, 0.80)
    else:
        theta, mirror, frac = 0.0, False, 0.6
    s = frac * size / ext
    half = 0.5 * frac * size * (abs(math.cos(theta)) + abs(math.sin(theta)))
    room = max(0.0, size / 2 - 2 - half)
    if aug and room > 0:
        tx, ty = rng.uniform(-room, room, 2)
    else:
        tx = ty = 0.0
    return theta, mirror, s, float(tx), float(ty)


def _xform(P, ctr, theta, mirror, s, tx, ty, size):
    Q = (P - ctr) * np.array([-1.0 if mirror else 1.0, 1.0], np.float32)
    c, sn = math.cos(theta), math.sin(theta)
    R = np.array([[c, -sn], [sn, c]], np.float32)
    return (Q @ R.T) * s + np.array([size / 2 + tx, size / 2 + ty], np.float32)


def _render(prof_px, mpts_px, mlines, size):
    pi = np.round(prof_px).astype(np.int32)
    outline = np.zeros((size, size), np.uint8)
    cv2.polylines(outline, [pi], True, 1, 1)
    filled = np.zeros((size, size), np.uint8)
    cv2.fillPoly(filled, [pi], 1)
    mid = np.zeros((size, size), np.uint8)
    mi = np.round(mpts_px).astype(int)
    for a, b in mlines:
        cv2.line(mid, (int(mi[a, 0]), int(mi[a, 1])), (int(mi[b, 0]), int(mi[b, 1])), 1, 1)
    return outline, filled, mid


def make_input(outline, filled):
    dt = ndi.distance_transform_edt(filled)
    dt = dt / max(float(dt.max()), 1e-6)
    return np.stack([outline, filled, dt]).astype(np.float32)


class MidcurveRaster(Dataset):
    """seed=None -> fresh random sample every call (train). seed=int -> deterministic per index (val/test),
    shapes cycled evenly."""

    def __init__(self, shapes, names, size=128, length=2000, aug=True, seed=None):
        self.shapes, self.names, self.size = shapes, list(names), size
        self.length, self.aug, self.seed = length, aug, seed
        self.ext = {n: float(np.ptp(shapes[n]["profile"], axis=0).max()) for n in self.names}
        self.ctr = {n: (shapes[n]["profile"].min(0) + shapes[n]["profile"].max(0)) / 2 for n in self.names}

    def __len__(self):
        return self.length

    def __getitem__(self, i):
        rng = np.random.default_rng(None if self.seed is None else [self.seed, i])
        if self.seed is None:
            name = self.names[int(rng.integers(len(self.names)))]
        else:
            name = self.names[i % len(self.names)]
        sh = self.shapes[name]
        theta, mirror, s, tx, ty = _pose(rng, self.size, self.ext[name], self.aug)
        prof = _xform(sh["profile"], self.ctr[name], theta, mirror, s, tx, ty, self.size)
        mpts = _xform(sh["mpts"], self.ctr[name], theta, mirror, s, tx, ty, self.size)
        outline, filled, mid = _render(prof, mpts, sh["mlines"], self.size)
        x = torch.from_numpy(make_input(outline, filled))
        y = torch.from_numpy(mid.astype(np.float32))[None]
        return x, y, name


def make_splits(shapes, holdout, size, n_train, n_val, n_test):
    """holdout None/'none': all shapes everywhere (pose-level generalisation only, state this in reports).
    holdout 'Plus': test on Plus only; train+val on the rest (val = new poses of seen shapes)."""
    names = sorted(shapes)
    if holdout in (None, "none"):
        tr = va = te = names
    else:
        te = [holdout]
        tr = [n for n in names if n != holdout]
        va = tr
    return (MidcurveRaster(shapes, tr, size, n_train, True, None),
            MidcurveRaster(shapes, va, size, n_val, True, 1234),
            MidcurveRaster(shapes, te, size, n_test, True, 5678))
```
Legacy-compatible reader (so the new tricks can be compared on the OLD 448 pairs; 100x100, ink in alpha,
split by filename prefix like `prepare_data.py:70-80`):

```python
# data.py (append)
from PIL import Image


class LegacyPairs(Dataset):
    def __init__(self, folder, shapes_keep, flip_aug=True):
        self.items = []
        for fn in sorted(os.listdir(folder)):
            if "Profile" in fn and fn.endswith(".png") and fn.split("_")[0] in shapes_keep:
                m = os.path.join(folder, fn.replace("Profile", "Midcurve"))
                if os.path.exists(m):
                    self.items.append((os.path.join(folder, fn), m, fn.split("_")[0]))
        self.flip_aug = flip_aug

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        p, m, name = self.items[i]
        outline = (np.asarray(Image.open(p).convert("RGBA"))[:, :, 3] > 127).astype(np.uint8)
        mid = (np.asarray(Image.open(m).convert("RGBA"))[:, :, 3] > 127).astype(np.uint8)
        filled = ndi.binary_fill_holes(outline).astype(np.uint8)
        x = make_input(outline, filled)
        y = mid.astype(np.float32)[None]
        if self.flip_aug:
            k = np.random.randint(4)
            x = np.rot90(x, k, (1, 2)).copy()
            y = np.rot90(y, k, (1, 2)).copy()
        return torch.from_numpy(x), torch.from_numpy(y), name
```
(Legacy size is 100; UNetLite needs a multiple of 2^depth, so pad to 112 or use depth 2; see `--pad` in
the driver. Simpler: do not use LegacyPairs for UNet.)

### T4. Fully convolutional UNet-lite with GroupNorm, CoordConv, concat skips (file `models.py`)
Replace the 8-level 1x1-bottleneck UNet with 4 levels (128 -> 8), about 1.5M parameters at base 24, GroupNorm
(batch-size independent, safe at batch 1), SiLU, bilinear upsample + conv (no checkerboard), concat skips
(no copy shortcut because the loss now punishes outline ink), optional Dropout2d in the bottleneck only.

```python
# models.py
import math
import torch
import torch.nn as nn
import torch.nn.functional as F


def gn(c):
    return nn.GroupNorm(8 if c % 8 == 0 else 1, c)


def block(cin, cout):
    return nn.Sequential(
        nn.Conv2d(cin, cout, 3, padding=1, bias=False), gn(cout), nn.SiLU(inplace=True),
        nn.Conv2d(cout, cout, 3, padding=1, bias=False), gn(cout), nn.SiLU(inplace=True))


class AddCoords(nn.Module):
    def forward(self, x):
        b, _, h, w = x.shape
        ys = torch.linspace(-1, 1, h, device=x.device, dtype=x.dtype).view(1, 1, h, 1).expand(b, 1, h, w)
        xs = torch.linspace(-1, 1, w, device=x.device, dtype=x.dtype).view(1, 1, 1, w).expand(b, 1, h, w)
        return torch.cat([x, xs, ys], 1)


class UNetLite(nn.Module):
    """skips=True -> 'unet'. skips=False -> plain conv encoder-decoder ('cnn')."""

    def __init__(self, in_ch=3, out_ch=1, base=24, depth=4, skips=True, coord=True, drop=0.1):
        super().__init__()
        self.coord = AddCoords() if coord else nn.Identity()
        c0 = in_ch + (2 if coord else 0)
        chs = [min(base * 2 ** i, 256) for i in range(depth + 1)]
        self.skips = skips
        self.enc = nn.ModuleList([block(c0 if i == 0 else chs[i - 1], chs[i]) for i in range(depth + 1)])
        self.dec = nn.ModuleList([block(chs[i + 1] + (chs[i] if skips else 0), chs[i]) for i in range(depth)])
        self.drop = nn.Dropout2d(drop) if drop > 0 else nn.Identity()
        self.head = nn.Conv2d(chs[0], out_ch, 1)
        nn.init.constant_(self.head.bias, -4.0)   # ~2 percent ink prior

    def forward(self, x):
        x = self.coord(x)
        feats = []
        for i, e in enumerate(self.enc):
            x = e(x if i == 0 else F.max_pool2d(x, 2))
            feats.append(x)
        x = self.drop(x)
        for i in reversed(range(len(self.dec))):
            x = F.interpolate(x, scale_factor=2, mode="bilinear", align_corners=False)
            if self.skips:
                x = torch.cat([x, feats[i]], 1)
            x = self.dec[i](x)
        return self.head(x)


class DenseAE(nn.Module):
    """Dense baselines. simple: Linear(d,code)-Linear(code,d). dense: 2048-1024-code-1024-2048."""

    def __init__(self, size=64, in_ch=3, code=128, deep=True):
        super().__init__()
        d = size * size * in_ch
        self.size = size
        if deep:
            enc = [nn.Linear(d, 1024), nn.GELU(), nn.Linear(1024, 512), nn.GELU(), nn.Linear(512, code), nn.GELU()]
            dec = [nn.Linear(code, 512), nn.GELU(), nn.Linear(512, 1024), nn.GELU(), nn.Linear(1024, size * size)]
        else:
            enc = [nn.Linear(d, code), nn.GELU()]
            dec = [nn.Linear(code, size * size)]
        self.enc, self.dec = nn.Sequential(*enc), nn.Sequential(*dec)
        nn.init.constant_(self.dec[-1].bias, -4.0)

    def forward(self, x):
        z = self.enc(x.flatten(1))
        return self.dec(z).view(-1, 1, self.size, self.size)


class PatchD(nn.Module):
    """Conditional PatchGAN with spectral norm (no BN, batch independent). Input: x (3ch) + y (1ch)."""

    def __init__(self, in_ch=4, base=32):
        super().__init__()
        sn = nn.utils.spectral_norm
        self.net = nn.Sequential(
            sn(nn.Conv2d(in_ch, base, 4, 2, 1)), nn.LeakyReLU(0.2, True),
            sn(nn.Conv2d(base, base * 2, 4, 2, 1)), nn.LeakyReLU(0.2, True),
            sn(nn.Conv2d(base * 2, base * 4, 4, 2, 1)), nn.LeakyReLU(0.2, True),
            sn(nn.Conv2d(base * 4, base * 4, 4, 1, 1)), nn.LeakyReLU(0.2, True),
            nn.Conv2d(base * 4, 1, 4, 1, 1))

    def forward(self, x, y):
        return self.net(torch.cat([x, y], 1))


ARCHS = ["simple", "dense", "cnn", "denoiser", "unet", "pix2pix", "skeleton"]
DEFAULT_SIZE = {"simple": 64, "dense": 64, "cnn": 128, "denoiser": 128, "unet": 128, "pix2pix": 128,
                "skeleton": 128}


def build_model(arch, size, in_ch=3):
    if arch == "simple":
        return DenseAE(size, in_ch, code=128, deep=False)
    if arch == "dense":
        return DenseAE(size, in_ch, code=128, deep=True)
    if arch == "cnn":
        return UNetLite(in_ch, base=32, depth=3, skips=False, drop=0.0)
    if arch in ("unet", "pix2pix"):
        return UNetLite(in_ch, base=24, depth=4, skips=True, drop=0.1)
    if arch == "denoiser":
        return UNetLite(in_ch, base=24, depth=3, skips=True, drop=0.0)  # in: noisy mid + outline + filled
    raise ValueError(arch)
```
Notes: 'cnn' with `skips=False` is the honest plain encoder-decoder (8x8 at 16 px per side is a real
bottleneck of 8x8x256 for 128 px: 16k values; use depth 3 -> 16x16x256 is as before, so keep depth 4,
base 24 if you want a tighter bottleneck; the driver exposes `--depth`). Expect `unet` > `cnn` > `dense`
> `simple` once the loss and input are fixed; that ordering is itself a finding for the paper.

### T5. Metrics that mean something (file `metrics.py`, `postproc.py`)
Per sample after thresholding + skeletonising: precision/recall/F1 "within tol px" (default 2 px at 128),
Chamfer (mean symmetric distance), Hausdorff (max), plus topology: number of connected components,
endpoints and junction clusters compared with the GT skeleton. Aggregate per shape and overall.

```python
# postproc.py
import numpy as np
from scipy import ndimage as ndi

_K8 = np.ones((3, 3), int)


def skeleton(mask):
    mask = mask.astype(bool)
    try:
        from skimage.morphology import skeletonize
        return skeletonize(mask)
    except ImportError:
        return mask


def to_polyline_mask(prob, thr=0.5, min_px=8):
    b = prob >= thr
    lab, n = ndi.label(b, structure=_K8)
    if n:
        sizes = ndi.sum(b, lab, index=np.arange(1, n + 1))
        b = np.isin(lab, 1 + np.where(sizes >= min_px)[0])
    return skeleton(b)


def topo_counts(skel):
    skel = skel.astype(bool)
    nb = ndi.convolve(skel.astype(int), _K8, mode="constant") * skel   # includes self
    ends = int(((nb == 2) & skel).sum())
    junc = ndi.label((nb >= 4) & skel, structure=_K8)[1]
    comps = ndi.label(skel, structure=_K8)[1]
    return comps, ends, junc
```
```python
# metrics.py
import numpy as np
from scipy import ndimage as ndi
from .postproc import to_polyline_mask, skeleton, topo_counts


def tolerance_scores(pred, gt, tol=2.0):
    pred, gt = pred.astype(bool), gt.astype(bool)
    diag = float(np.hypot(*gt.shape))
    if not pred.any():
        return dict(prec=0.0, rec=0.0, f1=0.0, chamfer=diag, hausdorff=diag)
    d_gt = ndi.distance_transform_edt(~gt)
    d_pr = ndi.distance_transform_edt(~pred)
    a, b = d_gt[pred], d_pr[gt]
    prec, rec = float((a <= tol).mean()), float((b <= tol).mean())
    f1 = 0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec)
    return dict(prec=prec, rec=rec, f1=f1, chamfer=float(0.5 * (a.mean() + b.mean())),
                hausdorff=float(max(a.max(), b.max())))


def sample_metrics(prob, y_thin, thr=0.5, tol=2.0):
    sk = to_polyline_mask(prob, thr)
    gk = skeleton(y_thin > 0.5)
    m = tolerance_scores(sk, gk, tol)
    m["topo_ok"] = float(topo_counts(sk) == topo_counts(gk))
    return m


def aggregate(rows):
    keys = ["prec", "rec", "f1", "chamfer", "hausdorff", "topo_ok"]
    out = {"all": {k: float(np.mean([r[k] for r in rows])) for k in keys}}
    for s in sorted({r["shape"] for r in rows}):
        sub = [r for r in rows if r["shape"] == s]
        out[s] = {k: float(np.mean([r[k] for r in sub])) for k in keys}
    return out
```
Report the "blank prediction" and `skeletonize(filled)` baselines in every table (T11). Render result grids
with a fixed 0..1 scale (add `fixed_scale=True` option to `save_results_grid_images`, or a new `viz.py`),
never per-cell autoscale, when judging quality.

### T6. Leave-one-shape-out + seen-shape/new-pose, reported separately
Two numbers per run: (a) `val`: seen shapes, new random poses (pose generalisation); (b) `test`: held-out
shape (shape generalisation). `--holdout all` loops over I, L, T, Plus and averages. This replaces
`TEST_SHAPES = ('Plus',)/VAL_SHAPES = ('T',)` in `prepare_data.py:66-67`, which would leave only I and L to
train on. State clearly in any write-up that 4 shapes cannot prove shape generalisation.

### T7. Test-time augmentation (8 dihedral transforms), nearly free
```python
@torch.no_grad()
def predict_tta(model, x, tta=True):
    ops = [(k, f) for k in range(4) for f in (False, True)] if tta else [(0, False)]
    acc = 0
    for k, f in ops:
        xi = torch.rot90(x, k, (2, 3))
        if f:
            xi = torch.flip(xi, (3,))
        p = torch.sigmoid(model(xi))
        if f:
            p = torch.flip(p, (3,))
        acc = acc + torch.rot90(p, -k, (2, 3))
    return acc / len(ops)
```
Typically +1-3 F1 points and cleaner junctions. Report with and without.

### T8. Optimiser and schedule
AdamW(lr 2e-3, wd 1e-4), `OneCycleLR` (max_lr 2e-3, `total_steps = epochs*len(loader)`), grad clip 1.0,
batch 16 (batch 1 is also safe with GroupNorm), 60 epochs x 125 steps = 7.5k steps for unet/cnn. Keep the
best epoch by `val` F1 (not loss). Seeds fixed.

### T9. Threshold tuning on val
Choose the binarisation threshold from {0.2..0.8} that maximises val F1; use it for test. 5 lines in the
driver. Replace the fixed 0.5.

### T10. Deep supervision / coarse-to-fine (optional)
Add 1x1 heads at decoder levels 1 and 2, upsample, apply the same `seg_loss` with weight 0.3 each. Helps
long-range line continuity. Skip unless T1-T9 plateau.

### T11. Classical baseline `--arch skeleton` (no learning)
`skeletonize(filled)` pruned of spurs, scored with the same metrics. If a model does not beat it, the model
is not learning anything the classical method does not already give. Needed for honest framing: a
medial-axis of a thick polygon is also what midcurve means in CAD, but it shortens line ends and sprouts
spurs at corners, which is where a learned model can win.

### T12. Denoiser done right (optional, after unet works)
Train on corrupted GT, not on stage-1 output of training data:
```python
def corrupt(y, g):
    """y: (B,1,H,W) thin GT. Returns a plausible 'bad stage-1 output'."""
    from .losses import blur
    s = blur(y, 1.0 + 2.0 * torch.rand((), generator=g).item())
    s = s / s.amax(dim=(2, 3), keepdim=True).clamp_min(1e-6)
    s = s * (0.3 + 0.7 * torch.rand(y.shape[0], 1, 1, 1, device=y.device))        # faint
    s = s + 0.08 * torch.randn_like(s)                                              # noise
    dx, dy = [int(v) for v in torch.randint(-2, 3, (2,))]
    s = torch.roll(s, (dy, dx), (2, 3))                                              # small shift
    return s.clamp(0, 1)
# denoiser input = cat([corrupt(y), x[:, :2]]) ; target = y
```
At evaluation chain it after a trained stage 1: `p1 = sigmoid(stage1(x)); p2 = sigmoid(den(cat([p1, x[:, :2]], 1)))`.

### T13. What to try only if still unsatisfied
Predict the signed distance to the nearest midcurve (heatmap regression) and extract the ridge by
non-maximum suppression; clDice loss; output at 2x resolution (pixel-shuffle head) for sub-pixel
accuracy; vectorise the skeleton into a polyline graph and hand over to the Phase II/III evaluation
(Chamfer/Hausdorff on coordinates) so image results are comparable with the text and graph models.

## 4. pix2pix / img2img specifics

Why weak (all points are in Section 2.6/2.7): blank-attractor L1 (x100), BN with batch 1 (Keras) or 4
(PyTorch), dropout always on (PyTorch), 335-1340 total steps, JPEG/RGB inputs, nearest-upscaled strokes,
leaked splits, no metric, no checkpoint (PyTorch). The architecture is not the problem.

Plan: do not maintain two GAN implementations. Fold both into `--arch pix2pix` in the new package:
- Generator = `UNetLite` (same as `--arch unet`), 3 input channels (outline, filled, DT), logits output.
- Discriminator = `PatchD` (spectral norm, no BN), conditioned on the 3-channel input.
- Losses: LSGAN adversarial (`mse`), reconstruction = `seg_loss` (BCE+Dice) with weight 10 instead of
  L1 x 100; adversarial weight 1. Real samples fed to D are the SOFT target (`soft_target(y)`), fake samples
  are `sigmoid(logits)`, so D cannot win by detecting "crisp vs blurry".
- Warm start: first 5 epochs `adv_w = 0` (pure seg loss), then ramp adv weight to 1 over 10 epochs.
- Optimisers: Adam(2e-4, betas 0.5/0.999) for both, constant lr (or cosine for G), batch 8-16.
- Same dataset, same metrics, same TTA. The honest question (already raised in `analysis_report.md`,
  "Design-level caveat") is whether a GAN beats the plain UNet on an exact-output task; expect it will not
  on F1/Chamfer, but may give crisper strokes. Report both.

Reference training step:
```python
def train_pix2pix_step(G, D, optG, optD, x, y, lam=10.0, adv_w=1.0, pos_w=10.0):
    from .losses import seg_loss, soft_target
    logits = G(x)
    fake = torch.sigmoid(logits)
    real = soft_target(y)
    # D
    dr, df = D(x, real), D(x, fake.detach())
    lossD = 0.5 * (((dr - 1) ** 2).mean() + (df ** 2).mean())
    optD.zero_grad(set_to_none=True); lossD.backward(); optD.step()
    # G
    dg = D(x, fake)
    lossG = adv_w * ((dg - 1) ** 2).mean() + lam * seg_loss(logits, y, pos_weight=pos_w)
    optG.zero_grad(set_to_none=True); lossG.backward(); optG.step()
    return lossD.item(), lossG.item()
```
Legacy GAN folders: leave untouched except (optionally) the two cheap fixes that matter if anyone still
runs them: `img2img/main_img2img_pytorch.py` add `torch.save(generator.state_dict(), ...)` at the end of
`model_training`, and make dropout follow `self.training` (`training=self.training`).

## 5. Standardisation: folders, driver, dataset, safe sequence

### 5.1 Naming rules
- Architecture ids (used in CLI, folder names, run names, checkpoint names): `simple`, `dense`, `cnn`,
  `denoiser`, `unet`, `pix2pix` (img2img is merged into pix2pix), plus `skeleton` (baseline).
  Lower-case, no hyphens, no underscores inside the id.
- Python modules: snake_case, one role per file (`data.py`, `models.py`, `losses.py`, `metrics.py`,
  `postproc.py`, `train.py`). Avoid generic names that collide on `sys.path` (`config.py`, `utils.py`, both
  already collide in this repo, see CLAUDE.md "config module name collision"); the new package is imported
  as `image_based.midcurve_img`.
- Dataset ids: `synthetic_<size>` (on-the-fly from brep JSON), `legacy_pairs_100` (= `data/image-pairs`),
  `legacy_combo_256` (= `data/images-combo`), `legacy_unet_256` (= `data/unet-splits`). Prefix `legacy_`
  means frozen, tracked, not regenerable casually.
- Run folders: `runs/<arch>__<data>__<holdout>__<tag>/` containing `best.pt`, `args.json`,
  `metrics.json`, `grid.png`, `log.csv`. `runs/` is git-ignored (user manages `.gitignore`).

### 5.2 Target layout (additive; nothing moved in the first pass)
```
src/image_based/
  README.md                  (updated: how to run the one driver)
  midcurve_img/              NEW. single PyTorch implementation of all six archs
    __init__.py
    data.py  models.py  losses.py  metrics.py  postproc.py  train.py
    test_midcurve_img.py
  runs/                      NEW, generated, git-ignored
  data/                      UNCHANGED (legacy_pairs_100 / legacy_combo_256 / legacy_unet_256)
  simpleencoderdecoder/ cnnencoderdecoder/ denseencoderdecoder/ denoiserencoderdecoder/
  unet/ pix2pix/ img2img/    LEGACY Keras/PyTorch code, FROZEN (add a one-line README note, no edits)
  testing/ kaggle/           UNCHANGED
```
Optional second pass (needs the user's explicit OK because it touches 4,344 tracked files and old tests):
move the seven legacy folders under `image_based/legacy/` and rename `data/image-pairs` ->
`data/legacy_pairs_100` etc. Recommendation: do NOT do this now. Value is cosmetic, risk is high
(`test_*.py` path hacks, `prepare_data.py` constants, CLAUDE.md, README tables, notebooks).

### 5.3 The one driver (CLI)
```
cd D:/Yogesh/GitHub/MidcurveNN/src
conda run -n genai python -m image_based.midcurve_img.train --arch unet --data synthetic --size 128 ^
    --holdout none --epochs 60 --bs 16 --steps 125 --loss bcedice --tta --tag base
```
Arguments: `--arch {simple,dense,cnn,denoiser,unet,pix2pix,skeleton}`, `--data {synthetic,legacy_pairs}`,
`--size` (default per arch: 64 for simple/dense, 128 otherwise), `--holdout {none,I,L,T,Plus,all}`,
`--epochs`, `--steps` (batches per epoch), `--bs`, `--lr`, `--loss {bcedice,focaldice}`,
`--pos-weight`, `--sigma`, `--depth`, `--base`, `--tta`, `--tol` (default 2), `--seed`, `--tag`,
`--quick` (epochs 2, steps 5, size 64, for smoke tests), `--eval-only CKPT`, `--stage1-ckpt CKPT` (denoiser
chain), `--device {auto,cpu,cuda}`, `--workers` (default 0, Windows safe), `--out runs`.

Reference driver (`train.py`; keep ASCII-only prints, Windows console):
```python
# train.py
import argparse, csv, json, os, time
import numpy as np
import torch
from torch.utils.data import DataLoader
from .data import load_shapes, make_splits, LegacyPairs
from .models import build_model, PatchD, ARCHS, DEFAULT_SIZE
from .losses import seg_loss
from .metrics import sample_metrics, aggregate, tolerance_scores
from .postproc import skeleton, topo_counts


def parse():
    p = argparse.ArgumentParser()
    p.add_argument("--arch", required=True, choices=ARCHS)
    p.add_argument("--data", default="synthetic", choices=["synthetic", "legacy_pairs"])
    p.add_argument("--size", type=int, default=0)
    p.add_argument("--holdout", default="none")
    p.add_argument("--epochs", type=int, default=60)
    p.add_argument("--steps", type=int, default=125)
    p.add_argument("--bs", type=int, default=16)
    p.add_argument("--lr", type=float, default=2e-3)
    p.add_argument("--loss", default="bcedice")
    p.add_argument("--pos-weight", type=float, default=10.0)
    p.add_argument("--sigma", type=float, default=1.2)
    p.add_argument("--tol", type=float, default=2.0)
    p.add_argument("--tta", action="store_true")
    p.add_argument("--quick", action="store_true")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--tag", default="run")
    p.add_argument("--device", default="auto")
    p.add_argument("--workers", type=int, default=0)
    p.add_argument("--out", default=os.path.join("image_based", "runs"))
    return p.parse_args()


@torch.no_grad()
def predict(model, x, tta):
    ops = [(k, f) for k in range(4) for f in (False, True)] if tta else [(0, False)]
    acc = 0
    for k, f in ops:
        xi = torch.rot90(x, k, (2, 3))
        xi = torch.flip(xi, (3,)) if f else xi
        p = torch.sigmoid(model(xi))
        p = torch.flip(p, (3,)) if f else p
        acc = acc + torch.rot90(p, -k, (2, 3))
    return acc / len(ops)


def run_eval(model, loader, dev, thr, tol, tta, arch):
    rows = []
    if model is not None:
        model.eval()
    for x, y, names in loader:
        if arch == "skeleton":
            probs = [skeleton(xi[1].numpy() > 0.5).astype(np.float32) for xi in x]
        else:
            probs = predict(model, x.to(dev), tta).cpu().numpy()[:, 0]
        for pi, yi, n in zip(probs, y.numpy()[:, 0], names):
            m = sample_metrics(pi, yi, thr, tol)
            m["shape"] = n
            rows.append(m)
    return aggregate(rows)


def main():
    a = parse()
    if a.quick:
        a.epochs, a.steps, a.size = 2, 5, 64
    size = a.size or DEFAULT_SIZE[a.arch]
    torch.manual_seed(a.seed); np.random.seed(a.seed)
    dev = torch.device("cuda" if (a.device == "auto" and torch.cuda.is_available()) else
                       ("cpu" if a.device == "auto" else a.device))
    shapes = load_shapes()
    holdouts = sorted(shapes) if a.holdout == "all" else [a.holdout]
    summary = {}
    for ho in holdouts:
        run = "%s__%s__%s__%s" % (a.arch, a.data, ho, a.tag)
        out = os.path.join(a.out, run); os.makedirs(out, exist_ok=True)
        tr, va, te = make_splits(shapes, ho, size, a.steps * a.bs, 64, 64)
        mk = lambda ds, sh: DataLoader(ds, batch_size=a.bs, shuffle=sh, num_workers=a.workers)
        trl, val, tel = mk(tr, False), mk(va, False), mk(te, False)
        model = None if a.arch == "skeleton" else build_model(a.arch, size).to(dev)
        best = -1.0
        if model is not None:
            opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
            sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=a.lr, total_steps=a.epochs * len(trl))
            log = open(os.path.join(out, "log.csv"), "w", newline=""); w = csv.writer(log)
            w.writerow(["epoch", "loss", "val_f1", "sec"])
            for ep in range(a.epochs):
                t0 = time.time(); model.train(); tot = 0.0
                for x, y, _ in trl:
                    x, y = x.to(dev), y.to(dev)
                    loss = seg_loss(model(x), y, a.pos_weight, a.sigma, kind=a.loss)
                    opt.zero_grad(set_to_none=True); loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    opt.step(); sched.step(); tot += loss.item()
                f1 = run_eval(model, val, dev, 0.5, a.tol, False, a.arch)["all"]["f1"]
                w.writerow([ep, tot / len(trl), f1, time.time() - t0]); log.flush()
                print("ep %d loss %.4f val_f1 %.3f" % (ep, tot / len(trl), f1))
                if f1 > best:
                    best = f1; torch.save(model.state_dict(), os.path.join(out, "best.pt"))
            model.load_state_dict(torch.load(os.path.join(out, "best.pt"), map_location=dev))
            thr = max([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
                      key=lambda t: run_eval(model, val, dev, t, a.tol, a.tta, a.arch)["all"]["f1"])
        else:
            thr = 0.5
        res = {"val_seen_shapes_new_poses": run_eval(model, val, dev, thr, a.tol, a.tta, a.arch),
               "test": run_eval(model, tel, dev, thr, a.tol, a.tta, a.arch), "thr": thr,
               "holdout": ho, "args": vars(a)}
        json.dump(res, open(os.path.join(out, "metrics.json"), "w"), indent=1)
        summary[ho] = res["test"]["all"]
        print(run, "TEST", res["test"]["all"])
    json.dump(summary, open(os.path.join(a.out, "summary_%s_%s.json" % (a.arch, a.tag)), "w"), indent=1)


if __name__ == "__main__":
    main()
```
The `pix2pix` branch (Section 4 step function, D optimiser, warm-up) and the `denoiser` corruption (T12)
are added inside the same loop by Sonnet (items 11 and 12). Result grids: call
`utils.prepare_plots.save_results_grid_images(inputs=outline channel, ground_truths, predictions, ...)`
for 7 test samples at the end of each run (needs `src/` on `sys.path`, true when run with `-m` from `src/`).
Add a `fixed_scale=True` keyword there (default False, so old callers do not change) or write a 15-line
`viz.py`.

### 5.4 Standard dataset definition (what every image model reads)
One sample = `(x, y, shape_name)`:
- `x`: float32 `[3,H,W]` = outline (1 px, ink 1), filled polygon, distance transform / its max.
- `y`: float32 `[1,H,W]`, 1-px midcurve ink 1, background 0. Blurring/weighting is done in the loss only.
- `H = W = size` (64/128/256, divisible by 16). Same transform applied to polygon and midcurve vertices
  before rasterising. Midcurve lines come from the brep `Lines` (branches handled).
- Splits are by shape NAME (never by file): `train` / `val` (new poses of train shapes) / `test` (held-out
  shape, or all shapes with fresh poses when `--holdout none`, labelled as pose-level).
Optional export for external tools (not needed for the new driver): PNGs `<split>/<shape>_<idx>_{in,filled,mid}.png`
plus `manifest.csv` (shape, split, idx, theta, mirror, scale, tx, ty). Write only on explicit request.

### 5.5 Safe data sequence (do NOT regenerate casually)
Facts: `drawsvg` is absent from the `genai` env; `image-pairs`, `unet-splits`, `images-combo` are 4,344
tracked files; `prepare_data.py` `__main__` (`:626-651`) does `shutil.rmtree` on `images-combo` and
`unet-splits` and regenerates the sequences JSON with `recreate_data=True`. Running it would silently
change all committed data and results.
1. Do not run `utils/prepare_data.py` as a script. Do not install `drawsvg`.
2. The new package needs none of those files: it reads `text_based/data/brep/*.json` (4 small tracked
   files) and rasterises in memory with OpenCV.
3. Legacy datasets stay frozen as the record of the old numbers. If an apples-to-apples comparison with
   legacy numbers is wanted, use `--data legacy_pairs` (read-only) and note it is 100x100 and pose-leaky.
4. If the user ever wants new on-disk datasets, produce them into a NEW folder (for example
   `image_based/data_v2/`) via an explicit export script, show a dry-run listing first, and never delete or
   overwrite the legacy folders.
5. Before any later cleanup of legacy data: confirm with the user (`D:\Yogesh\GitHub` rules: plan first,
   list the destination first, confirm sizes afterwards).

### 5.6 More shapes (needed for real generalisation claims, optional phase 2)
`utils/create_ds.py` already draws T, I, L, E, C, F with exact midcurves (OpenCV, 256 px, random sizes and
rotations; needs `imutils`). Port its `draw_*` geometry to polygon + midcurve vertex lists (E, C, F, U,
Z, H, plus random arm lengths/widths of I/L/T/Plus) and add them to the brep-style dict that `load_shapes`
returns. That raises the number of families from 4 to roughly 10-15, so leave-one-shape-out becomes
meaningful, and makes image results comparable with the Phase II/III datasets. This is a separate
decision for the user.

## 6. Action list for Sonnet (execute in order, one at a time, confirm with the user after each group)

Global rules for the executor: read-only on `legacy` folders (do not edit them); create files with the
Write tool only; no git commands; run Python only via `conda run -n genai python ...` from
`D:/Yogesh/GitHub/MidcurveNN/src`; ASCII-only print output; do not install packages without asking the
user; stop and report on any failed acceptance check.

1. Environment check (10 min). Run
   `conda run -n genai python -c "import torch, cv2, scipy, matplotlib, PIL; print(torch.__version__, cv2.__version__)"`
   and `conda run -n genai python -c "import skimage; print(skimage.__version__)"`.
   Acceptance: first command prints versions. If `skimage` is missing, tell the user and ask before running
   `conda install -n genai scikit-image` and before adding `scikit-image` to `src/environment.yml`
   (the code degrades to unskeletonised masks without it, which makes topology metrics unreliable).
   Do not use torchvision.
2. Package skeleton (5 min). Create `src/image_based/midcurve_img/__init__.py` (empty).
   Acceptance: `conda run -n genai python -c "import image_based.midcurve_img"` from `src/` succeeds.
3. `data.py` (30 min). Create `src/image_based/midcurve_img/data.py` from Section T3 (both code blocks,
   merged into one file with a single import header). Acceptance: a throwaway script run from `src/`
   (put it in the scratchpad, not the repo) that builds `make_splits(load_shapes(), "none", 128, 10, 10, 10)`,
   fetches `tr[0]`, `va[0]`, `va[0]` again, and asserts: x shape (3,128,128), y shape (1,128,128),
   `y.sum() > 10`, `x[1].sum() > y.sum()`, values equal between the two `va[0]` calls, and that
   `y` pixels lie inside the filled mask dilated by 2 px for all 4 shapes (index 0..3 of `va`).
   Also save one PNG montage of 4 shapes x (outline, filled, DT, midcurve) in the scratchpad and look at it.
4. `losses.py` (15 min). Create from T1. Acceptance: `seg_loss` returns a finite scalar for random logits
   and a thin line target; loss with logits = very negative everywhere is larger than loss with logits
   high on the line (sanity ordering assert); backward works.
5. `postproc.py` and `metrics.py` (30 min). Create from T5. Acceptance: for `pred == gt` F1 = 1,
   Chamfer 0, `topo_ok` = 1; for `pred` shifted by 1 px F1 = 1 at tol 2; for blank pred F1 = 0.
6. `models.py` (30 min). Create from T4. Acceptance: for each of `simple, dense, cnn, denoiser, unet, pix2pix`
   build the model at its default size, forward a batch of 2 and a batch of 1 (GroupNorm: batch 1 must
   work) and assert output shape (B,1,size,size); print parameter counts (expect unet about 1-2M, dense
   about 12M at size 64).
7. `train.py` for supervised archs + `skeleton` baseline (45 min). Create from Section 5.3. Acceptance:
   `conda run -n genai python -m image_based.midcurve_img.train --arch skeleton --quick --tag smoke` and
   `... --arch unet --quick --tag smoke` both finish, write `image_based/runs/<run>/metrics.json`, no
   exception. Report the skeleton baseline F1 per shape (this number is the floor to beat).
8. Unit tests (30 min). Create `src/image_based/midcurve_img/test_midcurve_img.py` (pytest, CPU, no
   TF): dataset determinism and shapes, loss ordering, metrics identities (item 5), model forward shapes
   for all archs, and an overfit test: `unet` at size 64, 8 fixed samples, 150 steps, `bcedice`, asserts
   train F1 at tol 2 > 0.8 (mark `slow` via a name, keep under 2 min). Add the directory to `src/pytest.ini`
   `testpaths` only after the user agrees. Acceptance:
   `python -m pytest image_based/midcurve_img -q` green; the existing 48 legacy tests unchanged.
9. First real experiments, pose-level (`--holdout none`) (about 1-3 h machine time, 20 min of attention).
   Run each with `--epochs 60 --steps 125 --tta` and tags `base`: `unet`, `cnn`, `dense`, `simple`.
   Record per-arch test F1, Chamfer, Hausdorff, topo_ok, seconds/epoch in
   `src/image_based/runs/summary_pose_level.csv` (create with Write; columns arch, f1, prec, rec, chamfer,
   hausdorff, topo_ok, sec_per_epoch). Acceptance targets (expectations, not guarantees): `unet` F1@2px
   >= 0.90 and beats `skeleton`; `cnn` >= 0.80; `dense`/`simple` lower. If `unet` F1 < 0.6 after 7.5k steps,
   stop and report the training curve (`log.csv`) instead of tuning blindly.
10. Ablation table, `unet` only, 20 epochs each, one change at a time (1 h): (a) loss `bcedice` vs plain BCE
    (`--pos-weight 1` and `dice_w 0` via a temporary flag), (b) input channels outline-only vs 3 channels
    (temporary `--in-ch 1` flag that zeroes channels 1,2), (c) no augmentation (`aug=False`), (d) TTA on/off,
    (e) `skips=False` (= `cnn`). Write to `runs/summary_ablation.csv`. Acceptance: file exists with 6 rows;
    report which trick moved F1 most (expected: loss and filled-mask input).
11. Shape-generalisation: run `--holdout all` for `unet` and `cnn` (30-60 min) and write
    `runs/summary_loso.csv` (columns holdout, arch, f1, chamfer, topo_ok). Acceptance: 4 holdouts x 2 archs.
    Report plainly that Plus held out has no 4-way junction in training and expect it to be the worst.
12. pix2pix branch (1.5 h). Extend `train.py` with `--arch pix2pix`: `PatchD`, step function from
    Section 4, `--adv-warmup 5`, save `best.pt` for G, evaluate G with the same `run_eval`. Acceptance:
    `--arch pix2pix --quick` runs; a 40-epoch run produces `metrics.json`; table row added to the pose-level
    csv. Compare against `unet` and say plainly which wins.
13. denoiser (1 h). Add `corrupt` (T12) and `--arch denoiser` training, plus `--stage1-ckpt` chained
    evaluation. Acceptance: chained F1 reported next to stage-1 alone; if not better, say so (do not tune).
14. Result grids (30 min). At end of each run write `grid.png` via
    `utils.prepare_plots.save_results_grid_images` with fixed 0..1 scale (add the optional
    `fixed_scale` keyword, default off, with a docstring line). Acceptance: open one grid and confirm that
    predictions are visibly crisp lines and that rows are input / GT / prediction.
15. Docs (30 min, only after the user agrees to the new layout). Update `src/image_based/README.md` (one
    section "Run all architectures with one command", the dataset-id table, the "legacy folders are frozen"
    note), add a short Phase I status paragraph to `CLAUDE.md` and `TODO.md` (include the correction that
    the UNet "best" claim is unsupported and the new numbers), and add an addendum to
    `src/image_based/analysis_report.md` with findings 2.3-2.7 not already listed. Acceptance: all commands
    in README run as written (copy-paste test of one `--quick` command).
16. Optional, only if the user asks: add `scikit-image` to `src/environment.yml`; port more shape families
    (Section 5.6); export on-disk dataset v2 (5.5 step 4); move legacy folders (5.2 second pass).
17. Final report to the user: table of all runs, what moved the needle, what did not, caveats (4 shapes,
    interpolation vs generalisation, tolerance 2 px at 128), list of new files for the user to commit
    (grouped: package code, tests, docs). Never run git.

Total estimate: about 6-8 h of Sonnet work plus about 3-6 h of unattended machine time (CPU; much less on
a GPU).

## 7. Decisions needed from the user (ask one at a time)

1. Adopt the new PyTorch package and freeze the Keras code? Recommended: yes (alternatives: patch the
   Keras models in place, or keep both). Reason: one loss/metric/dataset implementation for all six archs.
2. Image size default 128 (recommended) vs 100 (legacy) vs 256 (UNet legacy). 128 is the cheapest size
   where a 5-px wide arm and a 1-px line stay distinct.
3. Install `scikit-image` into `genai` and `environment.yml` (recommended: yes).
4. Whether to add more shape families now (5.6) or after the first results.
5. Whether to move legacy folders (recommended: not now).

## 8. Risks and caveats

- Midcurve ground truth for synthetic poses is exact only up to rounding to integer pixels (about 0.5 px);
  the 2 px tolerance absorbs this. Do not set the tolerance below 1 px.
- On the 4-shape data, high F1 in `--holdout none` is pose generalisation only. Say so wherever it is quoted.
- The skeleton of the filled polygon is a strong classical baseline for these simple shapes; a learned
  model is only interesting where it beats that baseline.
- `legacy_unet_256` contains the richer 6-family data; it cannot be shape-grouped (no shape id in file
  names), so it is excluded from the new driver except as an optional pose-level source.
- Windows: `num_workers=0` by default, ASCII prints only, forward slashes in paths, launch via
  `conda run -n genai python` (never the env python.exe directly).
- Numbers in Section 6 are targets from experience with similar thin-line segmentation problems, not
  measurements. Nothing in this document was trained or run.
