"""Architecture and checkpoint handling for the auto-LiRPA ResNet demo.

The architecture follows the user-supplied auto-LiRPA tutorial, originally
based on https://github.com/kuangliu/pytorch-cifar (MIT license).
See THIRD_PARTY_NOTICES.md. The teaching experiments live in the notebook.
"""

import hashlib
from pathlib import Path
from urllib.request import Request, urlopen

import torch
from torch import nn
from torch.nn import functional as F


CHECKPOINT_URL = (
    "https://download.huan-zhang.com/models/auto_lirpa/resnet18_natural.pth"
)
CHECKPOINT_SHA256 = "3ed98145186e9fcacf45a5335a8c6ab2f50e23fb673a73394b2e7bb3324ccf37"
CIFAR_MEAN = (0.4914, 0.4822, 0.4465)
CIFAR_STD = (0.2023, 0.1994, 0.2010)


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, in_planes, planes, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(
            in_planes, planes, 3, stride=stride, padding=1, bias=False
        )
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, 3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.shortcut = nn.Sequential()
        if stride != 1 or in_planes != planes:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_planes, planes, 1, stride=stride, bias=False),
                nn.BatchNorm2d(planes),
            )

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        return F.relu(out + self.shortcut(x))


class ResNet(nn.Module):
    def __init__(self, in_planes=2):
        super().__init__()
        self.in_planes = in_planes
        self.conv1 = nn.Conv2d(3, in_planes, 3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(in_planes)
        self.layer1 = self._make_layer(in_planes, stride=1)
        self.layer2 = self._make_layer(in_planes * 2, stride=2)
        self.layer3 = self._make_layer(in_planes * 4, stride=2)
        self.layer4 = self._make_layer(in_planes * 8, stride=2)
        self.linear = nn.Linear(in_planes * 8, 10)

    def _make_layer(self, planes, stride):
        layers = []
        for block_stride in (stride, 1):
            layers.append(BasicBlock(self.in_planes, planes, block_stride))
            self.in_planes = planes
        return nn.Sequential(*layers)

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = F.avg_pool2d(out, 4)
        return self.linear(out.flatten(1))


class PixelSpaceModel(nn.Module):
    """Accept raw [0, 1] pixels; include normalization in the verified graph."""

    def __init__(self, backbone):
        super().__init__()
        # Constants have no batch dimension; broadcasting adds it at runtime.
        self.register_buffer("mean", torch.tensor(CIFAR_MEAN).view(3, 1, 1))
        self.register_buffer("std", torch.tensor(CIFAR_STD).view(3, 1, 1))
        self.backbone = backbone

    def forward(self, pixels):
        return self.backbone((pixels - self.mean) / self.std)


def load_demo_model(device="cpu", data_dir="data"):
    """Cache the original demo weights, checking their SHA-256 before loading."""
    checkpoint_path = Path(data_dir) / "resnet18_natural.pth"
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    if not checkpoint_path.exists():
        request = Request(CHECKPOINT_URL, headers={"User-Agent": "ai-security-labs/1.0"})
        with urlopen(request, timeout=60) as response:
            content = response.read()
        if hashlib.sha256(content).hexdigest() != CHECKPOINT_SHA256:
            raise RuntimeError("Downloaded checkpoint does not match the lab checksum.")
        checkpoint_path.write_bytes(content)
    if hashlib.sha256(checkpoint_path.read_bytes()).hexdigest() != CHECKPOINT_SHA256:
        raise RuntimeError(f"Invalid checkpoint: remove {checkpoint_path} and rerun.")
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    backbone = ResNet()
    backbone.load_state_dict(checkpoint["state_dict"])
    return PixelSpaceModel(backbone).to(device).eval()
