# Img2Img (PyTorch Pix2Pix)

PyTorch implementation of the Pix2Pix GAN for profile→midcurve translation. Same architecture goal as `pix2pix/` but uses PyTorch, instance/batch normalization, and `torchvision.datasets.ImageFolder` for data loading.

**Architecture:** U-Net generator (8 encoder + 8 decoder blocks, skip connections) + PatchGAN discriminator; loss = BCE + 100× L1

**Input:** 256×512 side-by-side combo JPEGs from `data/images-combo/` (split at column 256 into profile and midcurve)
**Output:** 256×256 generated midcurve image

**Run:**
```bash
python image_based/img2img/main_img2img_pytorch.py
```

Results grid saved to `results/results_grid.png`. Intermediate training snapshots saved to `logs/`.
