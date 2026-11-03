"""Shared building blocks. GroupNorm only (never BatchNorm): batch size 1 must work."""
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
    """skips=True -> U-Net (concat skips). skips=False -> plain conv encoder-decoder."""

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


class FlatAE(nn.Module):
    """Fully connected autoencoder on the flattened [3,S,S] input -> [1,S,S] logits."""

    def __init__(self, size=128, in_ch=3, hidden=(), code=128):
        super().__init__()
        self.size = size
        d = size * size * in_ch
        enc, prev = [], d
        for h in hidden:
            enc += [nn.Linear(prev, h), nn.GELU()]
            prev = h
        enc += [nn.Linear(prev, code), nn.GELU()]
        dec, prev = [], code
        for h in reversed(hidden):
            dec += [nn.Linear(prev, h), nn.GELU()]
            prev = h
        dec += [nn.Linear(prev, size * size)]
        self.enc, self.dec = nn.Sequential(*enc), nn.Sequential(*dec)
        nn.init.constant_(self.dec[-1].bias, -4.0)

    def forward(self, x):
        z = self.enc(x.flatten(1))
        return self.dec(z).view(-1, 1, self.size, self.size)
