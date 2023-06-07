# Based on https://www.codespeedy.com/image-to-image-translation-in-pytorch/
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import math
import io

from PIL import Image
from copy import deepcopy
# from IPython.display import HTML

import torch
import torchvision
import torchvision.transforms as transforms
import torchvision.utils as vutils
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
manual_seed = 1028
random.seed(manual_seed)
torch.manual_seed(manual_seed)

log_path = os.path.join("./logs")  # Enter the log saving directory here
modelName = "pix2pix_pytorch"
data_path_Train = os.path.dirname('../data/pix2pix/train')  # Enter the train folder directory
data_path_Test = os.path.dirname('../data/pix2pix/test')  # Enter the test folder directory

batch_size = 4
num_workers = 2

transform = transforms.Compose([transforms.Resize((256, 512)),
                                transforms.ToTensor(),
                                transforms.Normalize((0.5,), (0.5,)), ])

load_Train = DataLoader(torchvision.datasets.ImageFolder(root=
                                                         data_path_Train, transform=transform),
                        batch_size=batch_size,
                        shuffle=True, num_workers=num_workers)

load_Test = DataLoader(torchvision.datasets.ImageFolder(root=
                                                        data_path_Test, transform=transform),
                       batch_size=batch_size,
                       shuffle=False, num_workers=num_workers)


def show_E2S(batch1, batch2, title1, title2):
    # edges
    plt.figure(figsize=(15, 15))
    plt.subplot(1, 2, 1)
    plt.axis("off")
    plt.title(title1)
    plt.imshow(np.transpose(vutils.make_grid(batch1, nrow=1, padding=5,
                                             normalize=True).cpu(), (1, 2, 0)))
    # shoes
    plt.subplot(1, 2, 2)
    plt.axis("off")
    plt.title(title2)
    plt.imshow(np.transpose(vutils.make_grid(batch2, nrow=1, padding=5,
                                             normalize=True).cpu(), (1, 2, 0)))


def split_image(img, size=256):
    return img[:, :, :, :size], img[:, :, :, size:]


inst_norm = True if batch_size == 1 else False  # instance normalization


def conv(in_channels, out_channels, kernel_size, stride=1, padding=0):
    return nn.Conv2d(in_channels, out_channels, kernel_size, stride=stride,
                     padding=padding)


def conv_n(in_channels, out_channels, kernel_size, stride=1, padding=0, inst_norm=False):
    if inst_norm == True:
        return nn.Sequential(nn.Conv2d(in_channels, out_channels, kernel_size,
                                       stride=stride, padding=padding), nn.InstanceNorm2d(out_channels,
                                                                                          momentum=0.1, eps=1e-5), )
    else:
        return nn.Sequential(nn.Conv2d(in_channels, out_channels, kernel_size,
                                       stride=stride, padding=padding), nn.BatchNorm2d(out_channels,
                                                                                       momentum=0.1, eps=1e-5), )


def tconv(in_channels, out_channels, kernel_size, stride=1, padding=0, output_padding=0, ):
    return nn.ConvTranspose2d(in_channels, out_channels, kernel_size, stride=stride,
                              padding=padding, output_padding=output_padding)


def tconv_n(in_channels, out_channels, kernel_size, stride=1, padding=0, output_padding=0, inst_norm=False):
    if inst_norm == True:
        return nn.Sequential(nn.ConvTranspose2d(in_channels, out_channels, kernel_size,
                                                stride=stride, padding=padding, output_padding=output_padding),
                             nn.InstanceNorm2d(out_channels, momentum=0.1, eps=1e-5), )
    else:
        return nn.Sequential(nn.ConvTranspose2d(in_channels, out_channels, kernel_size,
                                                stride=stride, padding=padding, output_padding=output_padding),
                             nn.BatchNorm2d(out_channels, momentum=0.1, eps=1e-5), )


dim_c = 3
dim_g = 64


# Generator
class Gen(nn.Module):
    def __init__(self, inst_norm=False):
        super(Gen, self).__init__()
        self.n1 = conv(dim_c, dim_g, 4, 2, 1)
        self.n2 = conv_n(dim_g, dim_g * 2, 4, 2, 1, inst_norm=inst_norm)
        self.n3 = conv_n(dim_g * 2, dim_g * 4, 4, 2, 1, inst_norm=inst_norm)
        self.n4 = conv_n(dim_g * 4, dim_g * 8, 4, 2, 1, inst_norm=inst_norm)
        self.n5 = conv_n(dim_g * 8, dim_g * 8, 4, 2, 1, inst_norm=inst_norm)
        self.n6 = conv_n(dim_g * 8, dim_g * 8, 4, 2, 1, inst_norm=inst_norm)
        self.n7 = conv_n(dim_g * 8, dim_g * 8, 4, 2, 1, inst_norm=inst_norm)
        self.n8 = conv(dim_g * 8, dim_g * 8, 4, 2, 1)

        self.m1 = tconv_n(dim_g * 8, dim_g * 8, 4, 2, 1, inst_norm=inst_norm)
        self.m2 = tconv_n(dim_g * 8 * 2, dim_g * 8, 4, 2, 1, inst_norm=inst_norm)
        self.m3 = tconv_n(dim_g * 8 * 2, dim_g * 8, 4, 2, 1, inst_norm=inst_norm)
        self.m4 = tconv_n(dim_g * 8 * 2, dim_g * 8, 4, 2, 1, inst_norm=inst_norm)
        self.m5 = tconv_n(dim_g * 8 * 2, dim_g * 4, 4, 2, 1, inst_norm=inst_norm)
        self.m6 = tconv_n(dim_g * 4 * 2, dim_g * 2, 4, 2, 1, inst_norm=inst_norm)
        self.m7 = tconv_n(dim_g * 2 * 2, dim_g * 1, 4, 2, 1, inst_norm=inst_norm)
        self.m8 = tconv(dim_g * 1 * 2, dim_c, 4, 2, 1)
        self.tanh = nn.Tanh()

    def forward(self, x):
        n1 = self.n1(x)
        n2 = self.n2(F.leaky_relu(n1, 0.2))
        n3 = self.n3(F.leaky_relu(n2, 0.2))
        n4 = self.n4(F.leaky_relu(n3, 0.2))
        n5 = self.n5(F.leaky_relu(n4, 0.2))
        n6 = self.n6(F.leaky_relu(n5, 0.2))
        n7 = self.n7(F.leaky_relu(n6, 0.2))
        n8 = self.n8(F.leaky_relu(n7, 0.2))
        m1 = torch.cat([F.dropout(self.m1(F.relu(n8)), 0.5, training=True), n7], 1)
        m2 = torch.cat([F.dropout(self.m2(F.relu(m1)), 0.5, training=True), n6], 1)
        m3 = torch.cat([F.dropout(self.m3(F.relu(m2)), 0.5, training=True), n5], 1)
        m4 = torch.cat([self.m4(F.relu(m3)), n4], 1)
        m5 = torch.cat([self.m5(F.relu(m4)), n3], 1)
        m6 = torch.cat([self.m6(F.relu(m5)), n2], 1)
        m7 = torch.cat([self.m7(F.relu(m6)), n1], 1)
        m8 = self.m8(F.relu(m7))

        return self.tanh(m8)


dim_d = 64


# Discriminator
class Disc(nn.Module):
    def __init__(self, inst_norm=False):
        super(Disc, self).__init__()
        self.c1 = conv(dim_c * 2, dim_d, 4, 2, 1)
        self.c2 = conv_n(dim_d, dim_d * 2, 4, 2, 1, inst_norm=inst_norm)
        self.c3 = conv_n(dim_d * 2, dim_d * 4, 4, 2, 1, inst_norm=inst_norm)
        self.c4 = conv_n(dim_d * 4, dim_d * 8, 4, 1, 1, inst_norm=inst_norm)
        self.c5 = conv(dim_d * 8, 1, 4, 1, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x, y):
        xy = torch.cat([x, y], dim=1)
        xy = F.leaky_relu(self.c1(xy), 0.2)
        xy = F.leaky_relu(self.c2(xy), 0.2)
        xy = F.leaky_relu(self.c3(xy), 0.2)
        xy = F.leaky_relu(self.c4(xy), 0.2)
        xy = self.c5(xy)

        return self.sigmoid(xy)


def weights_init(z):
    cls_name = z.__class__.__name__
    if cls_name.find('Conv') != -1 or cls_name.find('Linear') != -1:
        nn.init.normal_(z.weight.data, 0.0, 0.02)
        nn.init.constant_(z.bias.data, 0)
    elif cls_name.find('BatchNorm') != -1:
        nn.init.normal_(z.weight.data, 1.0, 0.02)
        nn.init.constant_(z.bias.data, 0)


BCE = nn.BCELoss()  # binary cross-entropy
L1 = nn.L1Loss()

# instance normalization
Gen = Gen(inst_norm).to(device)
Disc = Disc(inst_norm).to(device)

# optimizers
Gen_optim = optim.Adam(Gen.parameters(), lr=2e-4, betas=(0.5, 0.999))
Disc_optim = optim.Adam(Disc.parameters(), lr=2e-4, betas=(0.5, 0.999))


def compare_batches(batch1, batch2, title1, title2, batch3=None, title3=None):
    # batch1
    plt.figure(figsize=(15, 15))
    plt.subplot(1, 3, 1)
    plt.axis("off")
    plt.title(title1)
    plt.imshow(np.transpose(vutils.make_grid(batch1, nrow=1, padding=5,
                                             normalize=True).cpu(), (1, 2, 0)))
    # batch2
    plt.subplot(1, 3, 2)
    plt.axis("off")
    plt.title(title2)
    plt.imshow(np.transpose(vutils.make_grid(batch2, nrow=1, padding=5,
                                             normalize=True).cpu(), (1, 2, 0)))
    # third batch
    if batch3 is not None:
        plt.subplot(1, 3, 3)
        plt.axis("off")
        plt.title(title3)
        plt.imshow(np.transpose(vutils.make_grid(batch3, nrow=1, padding=5,
                                                 normalize=True).cpu(), (1, 2, 0)))


def model_training():
    fix_con, _ = next(iter(load_Test))
    fix_con = fix_con.to(device)
    fix_X, fix_y = split_image(fix_con)

    with torch.no_grad():
        fk = Gen(fix_X)
    compare_batches(fix_X, fk, "input image", "prediction", fix_y, "ground truth")

    img_list = []
    Disc_losses = Gen_losses = Gen_GAN_losses = Gen_L1_losses = []

    iter_per_plot = 50
    epochs = 5
    L1_lambda = 100.0

    for ep in range(epochs):
        for i, (data, _) in enumerate(load_Train):
            size = data.shape[0]

            x, y = split_image(data.to(device), 256)

            r_masks = torch.ones(size, 1, 30, 30).to(device)
            f_masks = torch.zeros(size, 1, 30, 30).to(device)

            # disc
            Disc.zero_grad()
            # real_patch
            r_patch = Disc(y, x)
            r_gan_loss = BCE(r_patch, r_masks)

            fake = Gen(x)
            # fake_patch
            f_patch = Disc(fake.detach(), x)
            f_gan_loss = BCE(f_patch, f_masks)

            Disc_loss = r_gan_loss + f_gan_loss
            Disc_loss.backward()
            Disc_optim.step()

            # gen
            Gen.zero_grad()
            f_patch = Disc(fake, x)
            f_gan_loss = BCE(f_patch, r_masks)

            L1_loss = L1(fake, y)
            Gen_loss = f_gan_loss + L1_lambda * L1_loss
            Gen_loss.backward()

            Gen_optim.step()

            if (i + 1) % iter_per_plot == 0:
                print(
                    'Epoch [{}/{}], Step [{}/{}], disc_loss: {:.4f}, gen_loss: {:.4f},Disc(real): {:.2f},' + \
                    'Disc(fake):{:.2f}, gen_loss_gan:{:.4f}, gen_loss_L1:{:.4f}'.format(
                        ep, epochs, i + 1, len(load_Train), Disc_loss.item(), Gen_loss.item(), r_patch.mean(),
                        f_patch.mean(), f_gan_loss.item(), L1_loss.item()))

                Gen_losses.append(Gen_loss.item())
                Disc_losses.append(Disc_loss.item())
                Gen_GAN_losses.append(f_gan_loss.item())
                Gen_L1_losses.append(L1_loss.item())

                with torch.no_grad():
                    Gen.eval()
                    fake = Gen(fix_X).detach().cpu()
                    Gen.train()
                figs = plt.figure(figsize=(10, 10))

                plt.subplot(1, 3, 1)
                plt.axis("off")
                plt.title("input image")
                plt.imshow(np.transpose(vutils.make_grid(fix_X, nrow=1, padding=5,
                                                         normalize=True).cpu(), (1, 2, 0)))

                plt.subplot(1, 3, 2)
                plt.axis("off")
                plt.title("generated image")
                plt.imshow(np.transpose(vutils.make_grid(fake, nrow=1, padding=5,
                                                         normalize=True).cpu(), (1, 2, 0)))

                plt.subplot(1, 3, 3)
                plt.axis("off")
                plt.title("ground truth")
                plt.imshow(np.transpose(vutils.make_grid(fix_y, nrow=1, padding=5,
                                                         normalize=True).cpu(), (1, 2, 0)))

                plt.savefig(os.path.join(log_path, modelName + "-" + str(ep) + ".png"))
                plt.close()
                img_list.append(figs)


def main():
    model_training()
    t_batch, _ = next(iter(load_Test))
    t_x, t_y = split_image(t_batch, 256)

    with torch.no_grad():
        Gen.eval()
        fk_batch = Gen(t_x.to(device))
    compare_batches(t_x, fk_batch, "input images", "predicted images", t_y, "ground truth")
    plt.show()


if __name__ == '__main__':
    main()
