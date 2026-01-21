# PAP-agentic-ai-sdk

This is the official SDK for the PAP agentic AI.

## Architecture Diagram 🏗️

Here is the high-level architecture of the system. Click the diagram to see the full-size version.

[![Architecture Diagram](assets/arch_diagram.png)](assets/arch_diagram.png)

# 🐍 Python Environment Setup

This project uses a **Python virtual environment (venv)** to manage its dependencies.
This ensures that the project's packages are isolated from your global Python installation, preventing conflicts.

---

## 🚀 Initial Setup (One-Time Only)

If you are cloning this project for the first time, you need to create the virtual environment.

1. Navigate to the project's root directory in your terminal.
2. Run the following command to create a virtual environment folder named `venv`:

```bash
python -m venv venv
```

## 🔑 Activating the Environment (Every Time)

Before you run any scripts (`main.py`, `server.py`, etc.) or install packages, you must activate the virtual environment in your terminal.

### On Windows

(Use Command Prompt or PowerShell)

```bash
.\venv\Scripts\activate
```

### On macOS / Linux

```bash
source venv/bin/activate
```

---

✅ You'll know the environment is active when you see **`(venv)`** at the beginning of your terminal prompt.
You can now proceed to run the application.

## Installation

To create an identical environment, run the following command:

```bash
pip install -r requirements.txt
```
