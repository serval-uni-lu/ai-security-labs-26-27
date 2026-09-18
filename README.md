# ai-security-labs-26-27

This is the repository for AI security labs given at the AI and Cybersecurity course for the Erasmus Mundus Joint Master in Cybersecurity, for the academic year 2026–2027.

Labs will be added throughout the course. Each lab has its own Python environment.

## Available labs

- [Lab 01 — Environment setup](src/01_environment_setup/): install the dependencies with uv and run your first notebook.

## 1. Install the tools

On Linux or macOS, use your usual terminal. On Windows, we recommend [WSL 2](https://learn.microsoft.com/en-us/windows/wsl/install/) with Ubuntu:

1. Install WSL 2 using the linked instructions, then open the Ubuntu terminal.
2. Install VS Code on Windows and its **WSL** extension from Microsoft (`ms-vscode-remote.remote-wsl`).
3. Run all commands below inside the Ubuntu terminal, including installing Git and uv. Clone the repository in your Linux home directory (`cd ~`).

Running `code .` from that terminal opens the lab in VS Code connected to WSL. Install the Python and Jupyter extensions in WSL when prompted, and select the lab's `.venv/bin/python` notebook kernel.

Install [Git](https://git-scm.com/downloads) and [Visual Studio Code](https://code.visualstudio.com/). In VS Code, install the **Python** extension from Microsoft (`ms-python.python`) and the **Jupyter** extension from Microsoft (`ms-toolsai.jupyter`).

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) to manage Python, dependencies, and virtual environments:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your terminal after installation, then check:

```bash
git --version
uv --version
```

## 2. Set up and open the lab

In your terminal, clone the repository, enter the lab folder, install its dependencies, and launch VS Code from that same folder:

```bash
git clone https://github.com/serval-uni-lu/ai-security-labs-26-27.git
cd ai-security-labs-26-27/src/01_environment_setup
uv sync
code .
```

uv downloads the required Python version if necessary and creates a `.venv` folder with the dependencies recorded in `uv.lock`. The first installation can take several minutes, including downloading PyTorch.

Lab 01 uses Python 3.8 and the package versions specified in its `pyproject.toml`. Keep these versions for the exercises.

If `code` is unavailable, use **File → Open Folder** in VS Code and select `src/01_environment_setup`.

## 3. Run the notebook

1. Open `01_environment_setup.ipynb`.
2. Click **Select Kernel** at the top right of the notebook.
3. Choose **Python Environments**, then the interpreter in this lab's `.venv` folder (`.venv/bin/python` on Linux, macOS, or WSL).
4. Run the cells in order. The notebook downloads a dataset and trains small models, so keep an internet connection available.

If imports fail, check that the notebook kernel belongs to this lab's `.venv` and that `uv sync` completed successfully.

## Getting future labs

From the repository folder, download new labs with:

```bash
git pull --ff-only
```

Save your exercise work before updating. If Git reports that local changes would be overwritten, commit or stash them before retrying; ask the teaching team if you need help.

Then follow the same sequence for the new lab: `cd` into its folder, run `uv sync`, and launch `code .`. Select that lab's `.venv` as the notebook kernel. Environments are separate for each lab.
