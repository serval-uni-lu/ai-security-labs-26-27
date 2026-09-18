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

## 2. Get the labs and set your name once

In the terminal for your platform, create a course folder in your home directory and clone the repository. On Windows, this keeps the files inside WSL:

```bash
mkdir -p ~/courses
cd ~/courses
git clone https://github.com/serval-uni-lu/ai-security-labs-26-27.git
cd ai-security-labs-26-27
```

If you already cloned the repository, enter its folder instead.

Create your personal settings file and open it in VS Code. `cp -n` keeps an existing `.env` file if you run this again:

```bash
cp -n .env.example .env
code .env
```

Fill in your **own first name and family name**, keeping the quotation marks. For example:

```dotenv
LAB_FIRST_NAME="Ada"
LAB_FAMILY_NAME="Lovelace"
```

Save the file (**Cmd+S** on macOS / **Ctrl+S** on Windows and Linux), then return to your terminal. These environment variables are loaded from `.env` by the preparation command below and reused for every lab. Git ignores `.env`, so your personal settings stay local.

## 3. Prepare your notebook and open the lab

From the repository root, enter the lab folder, install its dependencies, create your named notebook, and launch VS Code from that same folder:

```bash
cd src/01_environment_setup
uv sync
uv run --env-file ../../.env ../../scripts/prepare_lab.py
code .
```

uv downloads the required Python version if necessary and creates a `.venv` folder with the dependencies recorded in `uv.lock`. The first installation can take several minutes, including downloading PyTorch.

Lab 01 uses Python 3.8 and the package versions specified in its `pyproject.toml`. Keep these versions for the exercises.

Wait for each command to finish successfully before running the next. The preparation command copies each starter notebook in the lab to a filename containing your name, for example:

```text
01_environment_setup__submission_Ada_Lovelace.ipynb
```

Spaces and punctuation within names become hyphens; accented letters are kept. Work in this **named copy** and leave the starter notebook unchanged. The copy stays beside the starter so that relative file paths still work.

Re-running the preparation command keeps existing submission files, including your answers. Git ignores these files, so your notebook work does not modify the tracked starter notebooks. Teacher updates to a starter are not automatically merged into your personal copy.

The dot in `code .` means “open the current folder”, so VS Code opens directly inside lab 01.

## 4. Install the notebook extensions

In the VS Code window you just opened, click **Extensions** in the left sidebar, or press **Cmd+Shift+X** on macOS / **Ctrl+Shift+X** on Linux and Windows.

Search for each of these Microsoft extensions and click **Install**:

- **Python** (`ms-python.python`).
- **Jupyter** (`ms-toolsai.jupyter`).

On Windows/WSL, use **Install in WSL: Ubuntu** if shown, so the extensions run alongside the lab's Python environment. Wait for installation to finish before opening the notebook.

## 5. Run and submit your notebook

1. Open the notebook with **your name** in its filename (the `__submission_` copy).
2. Click **Select Kernel** at the top right of the notebook.
3. Choose **Python Environments**, then the interpreter in this lab's `.venv` folder (`.venv/bin/python` on Linux, macOS, or WSL).
4. Run the cells in order. The notebook downloads a dataset and trains small models, so keep an internet connection available.

If imports fail, check that the notebook kernel belongs to this lab's `.venv` and that `uv sync` completed successfully.

At the end of class, save your named notebook. Following the course submission instructions, upload a ZIP containing only the named notebook(s) you worked on to [Moodle](https://moodle.uni.lu/). Keep the filenames with your first and family names; do not include `.env`, `.venv`, or the unchanged starter notebooks. On macOS, right-click the selected notebook(s) in Finder and choose **Compress**. On Linux or WSL, you can use your file manager's archive option; WSL users can run `explorer.exe .` from the lab terminal to find the files in Windows Explorer.

If you already started working in the original notebook, use **Save As** to save your answers under the generated submission filename before restoring the original. Ask the teaching team for help if you are unsure which file contains your work.

## Getting future labs

From the repository folder, download new labs with:

```bash
git pull --ff-only
```

Your `.env` and named submission notebooks stay local and are ignored by Git. Save your notebook before pulling. If Git still reports changes to tracked files, ask the teaching team before discarding anything.

Then `cd` into the newly released lab folder and use the same commands:

```bash
uv sync
uv run --env-file ../../.env ../../scripts/prepare_lab.py
code .
```

Open the named submission copy and select that lab's `.venv` as the notebook kernel. Environments are separate for each lab; your name settings are shared across all labs.
