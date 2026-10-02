# Lab 03 — Certified robustness

In this **15–20 minute** practical, you run a small pretrained ResNet-18 on one
CIFAR-10 image, compare IBP and CROWN, and check a robustness certificate.
There are **two code-completion exercises** with three expressions to fill in;
all other code is provided. The practical follows the auto-LiRPA quick-start tutorial.

## Start the lab

From this directory:

```bash
uv sync --locked
code .
```

Open `03_certified_robustness.ipynb` and select the Python interpreter in this
directory's `.venv`. Run the cells in order, replacing the `...` placeholders
in the two exercise cells. Save your notebook and outputs locally. See the
[repository setup guide](../../README.md) for editor and operating-system setup.

This environment uses Python 3.11 and a pinned May 2026 auto-LiRPA revision.
PyTorch 2.8 / torchvision 0.23 are used on Linux, WSL and Apple silicon.
Intel macOS automatically uses PyTorch 2.2.2 / torchvision 0.17.2 instead.
NumPy 1.26 works with both. Use this lab's environment rather than Lab 02's
TensorFlow environment. The Linux/WSL installation uses CPU wheels; a GPU is
not required. The notebook also selects CUDA if a compatible CUDA-enabled
PyTorch installation is available.

The first run downloads the CIFAR-10 archive (about 163 MiB) and the original
tutorial checkpoint (about 204 KiB) over HTTPS into the ignored `data/` folder.
Later runs reuse the cache. The checkpoint's SHA-256 is checked before loading.
If downloads fail, check the connection and rerun the cell. If the notebook
reports an invalid checkpoint, remove `data/resnet18_natural.pth` and rerun.

## Sources

- [Original quick-start tutorial](http://PaperCode.cc/AutoLiRPA-Demo).
- [Official verification example at the pinned revision](https://github.com/Verified-Intelligence/auto_LiRPA/blob/a050a3d61f4cb68b108fa7f07dcb3e4d7ef304df/examples/vision/simple_verification.py).
- [auto-LiRPA documentation](https://auto-lirpa.readthedocs.io/en/latest/).
- [Architecture attribution and license](THIRD_PARTY_NOTICES.md).
