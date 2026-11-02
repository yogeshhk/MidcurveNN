"""pix2pix: conditional GAN. Generator = UNet-lite (same as `unet`), discriminator = spectral-norm
PatchGAN (no BatchNorm). Reconstruction term is the segmentation loss (BCE+Dice) instead of L1 x 100;
the adversarial term is LSGAN, with a warm-up (pure seg loss first, then a linear ramp).

Real samples shown to D are the SOFT target and fake samples are sigmoid(logits), so D cannot win by
detecting 'crisp vs blurry'. The generator is what build_model returns and what best.pt stores.
"""
import torch
import torch.nn as nn

from ._blocks import UNetLite
from losses import seg_loss, soft_target


class PatchD(nn.Module):
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


def build_model(cfg):
    return UNetLite(cfg.get("in_ch", 3), base=cfg.get("base", 24), depth=cfg.get("depth", 4),
                    skips=True, coord=True, drop=cfg.get("drop", 0.1))


class GANTrainer:
    def __init__(self, G, args, dev, steps_per_epoch):
        self.G = G
        self.D = PatchD().to(dev)
        self.a = args
        self.optG = torch.optim.Adam(G.parameters(), lr=args.lr, betas=(0.5, 0.999))
        self.optD = torch.optim.Adam(self.D.parameters(), lr=2e-4, betas=(0.5, 0.999))
        total = args.epochs * steps_per_epoch
        self.schedG = torch.optim.lr_scheduler.CosineAnnealingLR(self.optG, T_max=max(1, total))
        self.spe = steps_per_epoch
        self.last = {}

    def adv_weight(self, epoch):
        w0, ramp = self.a.adv_warmup, self.a.adv_ramp
        if epoch < w0:
            return 0.0
        return min(1.0, (epoch - w0 + 1) / max(1, ramp))

    def step(self, x, y, epoch):
        a = self.a
        adv_w = self.adv_weight(epoch)
        logits = self.G(x)
        fake = torch.sigmoid(logits)
        real = soft_target(y, a.sigma if a.sigma > 0 else 1.2)
        lossD = torch.zeros((), device=x.device)
        if adv_w > 0:
            dr, df = self.D(x, real), self.D(x, fake.detach())
            lossD = 0.5 * (((dr - 1) ** 2).mean() + (df ** 2).mean())
            self.optD.zero_grad(set_to_none=True)
            lossD.backward()
            self.optD.step()
        rec = seg_loss(logits, y, a.pos_weight, a.sigma, kind=a.loss)
        adv = ((self.D(x, fake) - 1) ** 2).mean() if adv_w > 0 else torch.zeros((), device=x.device)
        lossG = adv_w * adv + 10.0 * rec
        self.optG.zero_grad(set_to_none=True)
        lossG.backward()
        torch.nn.utils.clip_grad_norm_(self.G.parameters(), 1.0)
        self.optG.step()
        self.schedG.step()
        self.last = dict(lossD=float(lossD.item()), adv_w=adv_w)
        return float(rec.item())


def make_trainer(model, args, dev, steps_per_epoch):
    return GANTrainer(model, args, dev, steps_per_epoch)
