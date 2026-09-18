# Lab 01 — Environment setup

Follow the [setup instructions](../../README.md) to install uv, save your first and family names in the repository's `.env` file, and configure VS Code.

From the repository root, enter the lab folder, install its dependencies, create your named notebook, and launch VS Code:

```bash
cd src/01_environment_setup
uv sync
uv run --env-file ../../.env ../../scripts/prepare_lab.py
code .
```

Open `01_environment_setup__submission_FirstName_FamilyName.ipynb` (with your own names), select the Python interpreter in `.venv` as the notebook kernel, and run the cells in order. Leave `01_environment_setup.ipynb` unchanged so you can pull course updates.

The preparation command preserves existing submission files when run again. Save and submit your named notebook according to the [submission instructions](../../README.md#5-run-and-submit-your-notebook).

The notebook checks the installed packages, downloads a dataset, and trains models with scikit-learn and PyTorch.

This lab uses Python 3.12, selected automatically by uv. PyTorch 2.8 is used on Linux/WSL and Apple silicon Macs. Intel Macs automatically use PyTorch 2.2.2, the [last series with official Intel macOS builds](https://pytorch.org/blog/pytorch2-2/). NumPy stays at 1.26.4 for compatibility with the existing `mlc` dataset interface.

## Dataset download

The lab downloads LCLD from [serval-uni-lu/tabularbench on Hugging Face](https://huggingface.co/datasets/serval-uni-lu/tabularbench/tree/main/lcld_v2). The data CSV is about 187 MB. `lab_data.py` verifies the downloads and reuses valid cached files in `data/mlc/lcld_v2/`.

Keep the notebook in this lab folder so its helper module and environment are available. If a download fails, check your connection and rerun the data-loading cell; incomplete or invalid cached files are downloaded again.
