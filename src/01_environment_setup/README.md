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
