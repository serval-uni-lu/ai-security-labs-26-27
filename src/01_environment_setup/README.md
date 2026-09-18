# Lab 01 — Environment setup

Follow the [setup instructions](../../README.md) to install uv, create this lab's environment, and configure VS Code.

From the repository root, enter the lab folder, install its dependencies, and launch VS Code:

```bash
cd src/01_environment_setup
uv sync
code .
```

Open `01_environment_setup.ipynb`, select the Python interpreter in `.venv` as the notebook kernel, and run the cells in order.

The notebook checks the installed packages, downloads a dataset, and trains models with scikit-learn and PyTorch.
