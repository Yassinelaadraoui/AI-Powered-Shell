
# 🐚 DMH AI Shell – AI-Powered Cross-Platform Shell Wrapper

DMH AI Shell is a **cross-platform AI-enhanced shell wrapper** for **Linux/macOS (Bash)** and **Windows (PowerShell)**.
It allows you to use your shell as usual, but with **AI superpowers**:

✅ Write **plain English** and get real shell commands
✅ Auto-executes safe commands, asks confirmation for ⚠️ dangerous ones
✅ Explains what commands do before running
✅ Works seamlessly with your existing shell environment

---

## ✨ Features

* **Natural Language → Commands**

  * Example:

    ```
    list all files in folder
    ```

    → Runs `ls` on Linux/macOS or `dir` on Windows

* **Process Management**

  ```
  kill process on port 3000
  ```

  → Returns the correct `lsof` + `kill` (Linux/macOS) or `Stop-Process` (Windows) command

* **Networking**

  ```
  show me my IP address
  ```

  → Suggests the right command per OS

* **Safety First**

  * Commands marked `SAFE: ✅` run automatically
  * Commands marked `SAFE: ⚠️` (like `rm -rf`, `kill -9`, `Remove-Item -Force`) require confirmation

* **Still a Shell**

  * Any valid shell command works directly
  * Example:

    ```
    ls -la
    git status
    ```

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/Yassinelaadraoui/AI-Powered-Shell.git
cd AI-Powered-Shell
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Set your **OpenRouter API Key**:

* [Get one here](https://openrouter.ai/)

**Linux/macOS (bash):**

```bash
export OPENROUTER_API_KEY="your_api_key_here"
```

**Windows (PowerShell):**

```powershell
setx OPENROUTER_API_KEY "your_api_key_here"
```

---

## 🚀 Usage

Run the shell:

```bash
python dmh_ai_shell.py
```

### Examples

**Natural Language:**

```
> list all files bigger than 100 MB
```

**Output:**

```
COMMAND:
find . -type f -size +100M

EXPLANATION:
Finds all files in the current folder larger than 100 MB.

SAFE:
✅
⚙️ Running: find . -type f -size +100M
```

---

**Unsafe Command (confirmation required):**

```
> delete all files in this folder
```

**Output:**

```
COMMAND:
rm -rf *

EXPLANATION:
Deletes all files and directories in the current folder recursively.

SAFE:
⚠️ This is destructive and will permanently delete files.
Run anyway? (y/N):
```

---

**Normal Shell:**

```
> git status
> ls -la
> dir
```

---

## ⚙️ Special Commands

* `:showkey` → Show current API key (masked)
* `:setkey <key>` → Update API key
* `:showmodel` → Show default model
* `:setmodel <model>` → Change default model (e.g., `openai/gpt-4o-mini`)
* `:creator` → Show project info
* `exit` → Quit the shell

---

## 🧠 How It Works

1. Input is read from the REPL.
2. If it’s a known shell command → runs directly.
3. If not → sent to OpenRouter with a strict system prompt:

   * Returns `COMMAND`, `EXPLANATION`, and `SAFE`.
4. ✅ safe commands run automatically.
5. ⚠️ unsafe commands require confirmation.

---

## 📜 License

MIT License © 2025 Yassine Laadraoui

---
