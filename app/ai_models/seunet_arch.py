"""
สถาปัตยกรรม SEUNet แบบ standalone (คัดลอกมาจาก models/unet/SE_Layer.py และ models/unet/SE_UNet.py
ในโปรเจกต์หลัก) เพื่อให้โฟลเดอร์ deploy/ นี้ใช้งานได้เอง ไม่ต้องพึ่งพาโค้ดอื่นในโปรเจกต์
"""
import torch
from torch import nn
from torch.nn import functional as F


class BasicConv2d(nn.Module):
    def __init__(self, in_channels, out_channels, **kwargs):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, bias=False, **kwargs)
        self.norm = nn.InstanceNorm2d(out_channels, affine=True)

    def forward(self, x):
        x = self.conv(x)
        x = self.norm(x)
        x = F.relu(x, inplace=True)
        return x


class FastSmoothSENorm(nn.Module):
    class SEWeights(nn.Module):
        def __init__(self, in_channels, reduction=2):
            super().__init__()
            self.conv1 = nn.Conv2d(in_channels, in_channels // reduction, kernel_size=1, stride=1, padding=0, bias=True)
            self.conv2 = nn.Conv2d(in_channels // reduction, in_channels, kernel_size=1, stride=1, padding=0, bias=True)

        def forward(self, x):
            b, c, h, w = x.size()
            out = torch.mean(x.view(b, c, -1), dim=-1).view(b, c, 1, 1)
            out = F.relu(self.conv1(out))
            out = self.conv2(out)
            return out

    def __init__(self, in_channels, reduction=2):
        super().__init__()
        self.norm = nn.InstanceNorm2d(in_channels, affine=False)
        self.gamma = self.SEWeights(in_channels, reduction)
        self.beta = self.SEWeights(in_channels, reduction)

    def forward(self, x):
        gamma = torch.sigmoid(self.gamma(x))
        beta = torch.tanh(self.beta(x))
        x = self.norm(x)
        return gamma * x + beta


class FastSmoothSeNormConv2d(nn.Module):
    def __init__(self, in_channels, out_channels, reduction=2, **kwargs):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, bias=True, **kwargs)
        self.norm = FastSmoothSENorm(out_channels, reduction)

    def forward(self, x):
        x = self.conv(x)
        x = F.relu(x, inplace=True)
        x = self.norm(x)
        return x


class RESseNormConv2d(nn.Module):
    def __init__(self, in_channels, out_channels, reduction=2, **kwargs):
        super().__init__()
        self.conv1 = FastSmoothSeNormConv2d(in_channels, out_channels, reduction, **kwargs)
        if in_channels != out_channels:
            self.res_conv = FastSmoothSeNormConv2d(in_channels, out_channels, reduction, kernel_size=1, stride=1, padding=0)
        else:
            self.res_conv = None

    def forward(self, x):
        residual = self.res_conv(x) if self.res_conv else x
        x = self.conv1(x)
        x += residual
        return x


class UpConv(nn.Module):
    def __init__(self, in_channels, out_channels, reduction=2, scale=2):
        super().__init__()
        self.scale = scale
        self.conv = FastSmoothSeNormConv2d(in_channels, out_channels, reduction, kernel_size=1, stride=1, padding=0)

    def forward(self, x):
        x = self.conv(x)
        x = F.interpolate(x, scale_factor=self.scale, mode="bilinear", align_corners=False)
        return x


class SEUNet(nn.Module):
    def __init__(self, in_channels=1, n_cls=2, n_filters=64, reduction=2, return_logits=False):
        super().__init__()
        self.in_channels = in_channels
        self.n_cls = 1 if n_cls == 2 else n_cls
        self.n_filters = n_filters
        self.return_logits = return_logits

        self.block_1_1_left = RESseNormConv2d(in_channels, n_filters, reduction, kernel_size=7, stride=1, padding=3)
        self.block_1_2_left = RESseNormConv2d(n_filters, n_filters, reduction, kernel_size=3, stride=1, padding=1)

        self.pool_1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.block_2_1_left = RESseNormConv2d(n_filters, 2 * n_filters, reduction, kernel_size=3, stride=1, padding=1)
        self.block_2_2_left = RESseNormConv2d(2 * n_filters, 2 * n_filters, reduction, kernel_size=3, stride=1, padding=1)
        self.block_2_3_left = RESseNormConv2d(2 * n_filters, 2 * n_filters, reduction, kernel_size=3, stride=1, padding=1)

        self.pool_2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.block_3_1_left = RESseNormConv2d(2 * n_filters, 4 * n_filters, reduction, kernel_size=3, stride=1, padding=1)
        self.block_3_2_left = RESseNormConv2d(4 * n_filters, 4 * n_filters, reduction, kernel_size=3, stride=1, padding=1)
        self.block_3_3_left = RESseNormConv2d(4 * n_filters, 4 * n_filters, reduction, kernel_size=3, stride=1, padding=1)

        self.pool_3 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.block_4_1_left = RESseNormConv2d(4 * n_filters, 8 * n_filters, reduction, kernel_size=3, stride=1, padding=1)
        self.block_4_2_left = RESseNormConv2d(8 * n_filters, 8 * n_filters, reduction, kernel_size=3, stride=1, padding=1)
        self.block_4_3_left = RESseNormConv2d(8 * n_filters, 8 * n_filters, reduction, kernel_size=3, stride=1, padding=1)

        self.pool_4 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.block_5_1_left = RESseNormConv2d(8 * n_filters, 16 * n_filters, reduction, kernel_size=3, stride=1, padding=1)
        self.block_5_2_left = RESseNormConv2d(16 * n_filters, 16 * n_filters, reduction, kernel_size=3, stride=1, padding=1)
        self.block_5_3_left = RESseNormConv2d(16 * n_filters, 16 * n_filters, reduction, kernel_size=3, stride=1, padding=1)

        self.upconv_4 = nn.ConvTranspose2d(16 * n_filters, 8 * n_filters, kernel_size=3, stride=2, padding=1, output_padding=1)
        self.block_4_1_right = FastSmoothSeNormConv2d((8 + 8) * n_filters, 8 * n_filters, reduction, kernel_size=3, stride=1, padding=1)
        self.block_4_2_right = FastSmoothSeNormConv2d(8 * n_filters, 8 * n_filters, reduction, kernel_size=3, stride=1, padding=1)
        self.vision_4 = UpConv(8 * n_filters, n_filters, reduction, scale=8)

        self.upconv_3 = nn.ConvTranspose2d(8 * n_filters, 4 * n_filters, kernel_size=3, stride=2, padding=1, output_padding=1)
        self.block_3_1_right = FastSmoothSeNormConv2d((4 + 4) * n_filters, 4 * n_filters, reduction, kernel_size=3, stride=1, padding=1)
        self.block_3_2_right = FastSmoothSeNormConv2d(4 * n_filters, 4 * n_filters, reduction, kernel_size=3, stride=1, padding=1)
        self.vision_3 = UpConv(4 * n_filters, n_filters, reduction, scale=4)

        self.upconv_2 = nn.ConvTranspose2d(4 * n_filters, 2 * n_filters, kernel_size=3, stride=2, padding=1, output_padding=1)
        self.block_2_1_right = FastSmoothSeNormConv2d((2 + 2) * n_filters, 2 * n_filters, reduction, kernel_size=3, stride=1, padding=1)
        self.block_2_2_right = FastSmoothSeNormConv2d(2 * n_filters, 2 * n_filters, reduction, kernel_size=3, stride=1, padding=1)
        self.vision_2 = UpConv(2 * n_filters, n_filters, reduction, scale=2)

        self.upconv_1 = nn.ConvTranspose2d(2 * n_filters, 1 * n_filters, kernel_size=3, stride=2, padding=1, output_padding=1)
        self.block_1_1_right = FastSmoothSeNormConv2d((1 + 1) * n_filters, n_filters, reduction, kernel_size=3, stride=1, padding=1)
        self.block_1_2_right = FastSmoothSeNormConv2d(n_filters, n_filters, reduction, kernel_size=3, stride=1, padding=1)

        self.conv1x1 = nn.Conv2d(1 * n_filters, self.n_cls, kernel_size=1, stride=1, padding=0)

    def forward(self, x):
        ds0 = self.block_1_2_left(self.block_1_1_left(x))
        ds1 = self.block_2_3_left(self.block_2_2_left(self.block_2_1_left(self.pool_1(ds0))))
        ds2 = self.block_3_3_left(self.block_3_2_left(self.block_3_1_left(self.pool_2(ds1))))
        ds3 = self.block_4_3_left(self.block_4_2_left(self.block_4_1_left(self.pool_3(ds2))))
        x = self.block_5_3_left(self.block_5_2_left(self.block_5_1_left(self.pool_4(ds3))))

        x = self.block_4_2_right(self.block_4_1_right(torch.cat([self.upconv_4(x), ds3], 1)))
        sv4 = self.vision_4(x)

        x = self.block_3_2_right(self.block_3_1_right(torch.cat([self.upconv_3(x), ds2], 1)))
        sv3 = self.vision_3(x)

        x = self.block_2_2_right(self.block_2_1_right(torch.cat([self.upconv_2(x), ds1], 1)))
        sv2 = self.vision_2(x)

        x = self.block_1_1_right(torch.cat([self.upconv_1(x), ds0], 1))
        x = x + sv4 + sv3 + sv2
        x = self.block_1_2_right(x)

        x = self.conv1x1(x)

        if self.return_logits:
            return x
        if self.n_cls == 1:
            return torch.sigmoid(x)
        return x
