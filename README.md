# ai-security-labs-26-27

This is the repository for AI security labs given at the AI and Cybersecurity course for the Erasmus Mundus Joint Master in Cybersecurity, for the academic year 2026–2027.

Labs will be added throughout the course. Each lab has its own Python environment.

## Available labs

- [Lab 01 — Environment setup](src/01_environment_setup/): install the dependencies with uv and run your first notebook.

## 1. Install the tools

Choose your operating system below, then continue with **Install uv**. If a tool is already installed, you can skip its installation.

### macOS

1. Download [VS Code for macOS](https://code.visualstudio.com/download). The **Universal** build works on both Intel and Apple silicon Macs.
2. Open the download, move **Visual Studio Code.app** into **Applications**, and launch it from there.
3. In VS Code, press **Cmd+Shift+P** to open the Command Palette. Search for and select **Shell Command: Install 'code' command in PATH**. This enables `code .` in your terminal. See the [official macOS instructions](https://code.visualstudio.com/docs/setup/mac).
4. Open **Terminal** using Spotlight (**Cmd+Space**, type `Terminal`, press Enter). If it was already open, quit and reopen it after the previous step.
5. Check Git:

```bash
git --version
```

If macOS asks to install Command Line Tools, accept and wait for installation to finish. You can also start the installation with:

```bash
xcode-select --install
```

Then run `git --version` again. These tools include Git; see [Git's macOS installation guide](https://git-scm.com/install/mac).

Use this Terminal app for the remaining commands. uv will install the lab's Python version for you.

### Windows — WSL 2 with Ubuntu

First, set up [WSL 2](https://learn.microsoft.com/en-us/windows/wsl/install/). Open **PowerShell as Administrator** from the Start menu and run:

```powershell
wsl --install -d Ubuntu
```

Restart your computer if prompted. Open **Ubuntu** from the Start menu and finish creating your Linux username and password. When typing a Linux password, characters are not displayed.

Install the editor on Windows:

1. Download the [VS Code Windows User Installer](https://code.visualstudio.com/download), run it, and leave **Add to PATH** enabled.
2. Launch VS Code. Open the **Extensions** view with **Ctrl+Shift+X**, search for **WSL** by Microsoft (`ms-vscode-remote.remote-wsl`), and click **Install**.
3. Close and reopen the Ubuntu terminal so it picks up the `code` command.

From now on, run the lab commands in **Ubuntu**, including Git and uv installation. In that terminal, install Git and curl:

```bash
sudo apt update
sudo apt install git curl
```

Later, `code .` will open the lab in a VS Code window connected to Ubuntu. Look for **WSL: Ubuntu** in the bottom-left corner. See the [official VS Code and WSL guide](https://code.visualstudio.com/docs/remote/wsl) if connecting fails.

### Linux

Open your terminal. On Ubuntu or Debian, install Git and curl:

```bash
sudo apt update
sudo apt install git curl
```

Download the **.deb** installer from the [VS Code download page](https://code.visualstudio.com/download), open it in your software installer, and choose **Install**. Then reopen your terminal.

For other distributions, install Git and curl with your distribution's package manager and follow the [VS Code Linux installation instructions](https://code.visualstudio.com/docs/setup/linux) for the appropriate package.

### Install uv — all platforms

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) to manage Python, dependencies, and virtual environments:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Run this in macOS Terminal, your Linux terminal, or Ubuntu on WSL. Restart that terminal after installation, then check:

```bash
git --version
uv --version
code --version
```

All three commands should print a version. If `uv` is not found, follow the shell setup message printed by its installer. If `code` is not found on macOS, repeat the Command Palette step above; on Windows, check **Add to PATH** in the VS Code installer and reopen Ubuntu.

## 2. Set up and open the lab

In the terminal for your platform, create a course folder in your home directory, clone the repository, enter the lab folder, install its dependencies, and launch VS Code from that same folder. On Windows, this keeps the files inside WSL:

```bash
mkdir -p ~/courses
cd ~/courses
git clone https://github.com/serval-uni-lu/ai-security-labs-26-27.git
cd ai-security-labs-26-27/src/01_environment_setup
uv sync
code .
```

uv downloads the required Python version if necessary and creates a `.venv` folder with the dependencies recorded in `uv.lock`. The first installation can take several minutes, including downloading PyTorch.

Lab 01 uses Python 3.8 and the package versions specified in its `pyproject.toml`. Keep these versions for the exercises.

Wait for `uv sync` to finish successfully before running `code .`. The dot means “open the current folder”, so VS Code opens directly inside lab 01.

If you already cloned the repository, use `cd` to enter its `src/01_environment_setup` folder, then run just `uv sync` and `code .`.

## 3. Install the notebook extensions

In the VS Code window you just opened, click **Extensions** in the left sidebar, or press **Cmd+Shift+X** on macOS / **Ctrl+Shift+X** on Linux and Windows.

Search for each of these Microsoft extensions and click **Install**:

- **Python** (`ms-python.python`).
- **Jupyter** (`ms-toolsai.jupyter`).

On Windows/WSL, use **Install in WSL: Ubuntu** if shown, so the extensions run alongside the lab's Python environment. Wait for installation to finish before opening the notebook.

## 4. Run the notebook

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
