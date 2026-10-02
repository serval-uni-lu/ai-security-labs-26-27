# Lab 03 — Certified robustness

An introductory practical based on the auto-LiRPA quick-start tutorial. Students
run a small pretrained ResNet-18 on CIFAR-10, compare IBP and CROWN, read
robustness certificates, and compare them with a supplied PGD attack.
Allow about 60–90 minutes. The three exercises ask for short explanations and
small changes to the experiment; the short gradient extension is optional.

## Start the lab

From this directory, after filling in the repository's `.env` file:

```bash
uv sync --locked
uv run --env-file ../../.env ../../scripts/prepare_lab.py
code .
```

Open your named `__submission_` notebook and select the Python interpreter in
this directory's `.venv`. Run the cells in order and write your answers in the
three exercise cells. Save the outputs, then submit your named notebook using
the course's Moodle instructions. See the [repository setup guide](../../README.md)
for editor and operating-system setup.

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

## Teaching notes

The core notebook provides all implementations. Students need to interpret
outputs and change `EPSILON_LEVELS`, rather than implement a verifier or attack.
Use `RUN_EXTENSION = False` for the introductory session. A small naturally
trained model helps illustrate loose bounds and the distinction between
certified, attacked, and unresolved inputs.

Epsilon is defined on raw continuous pixels in `[0, 1]`, with normalization
inside the model. Certification checks all nine true-class margins and uses
a positive numerical tolerance. Batch normalization stays in evaluation mode.
The sweep concerns one fixed image: it does not estimate test-set accuracy or
the exact robust radius.

The local instructor notebook is
`03_certified_robustness__correction.ipynb`. It contains solutions, executed
results, the extra radii from Exercise 3, and the optional extension. It is
ignored by Git; keep it out of student distribution archives.

## Sources

- [Original quick-start tutorial](http://PaperCode.cc/AutoLiRPA-Demo).
- [Official verification example at the pinned revision](https://github.com/Verified-Intelligence/auto_LiRPA/blob/a050a3d61f4cb68b108fa7f07dcb3e4d7ef304df/examples/vision/simple_verification.py).
- [auto-LiRPA documentation](https://auto-lirpa.readthedocs.io/en/latest/).
- [Architecture attribution and license](THIRD_PARTY_NOTICES.md).
