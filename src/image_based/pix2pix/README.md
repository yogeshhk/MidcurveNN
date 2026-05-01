# Pix2Pix GAN (Keras)

Conditional GAN for profile→midcurve image-to-image translation. Generator is a U-Net (7-level); discriminator is a PatchGAN (16×16 patch decisions). Based on the Keras-GAN implementation.

**Architecture:** U-Net generator + PatchGAN discriminator; combined loss = MSE (adversarial) + 100× MAE (pixel)

**Input:** 256×256 side-by-side combo JPEGs from `data/images-combo/` (profile|midcurve concatenated)
**Output:** 256×256 generated midcurve image

**Run (from `src/`):**
```bash
python image_based/pix2pix/main_pix2pix.py
```

Results grid saved to `results/results_grid.png`. Intermediate sample images saved to `images/pix2pix/` during training.
