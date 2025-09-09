
# DMH AI Shell with OpenRouter Integration

🚀 **DMH AI Shell** is a Python-based interactive shell wrapper that integrates with the **OpenRouter API** to provide AI-powered assistance. It allows you to execute normal shell commands while also querying an LLM for explanations, suggestions, and debugging.  

---

## Features

- **Interactive shell**: Execute standard shell commands (`ls`, `dir`, `ping`, etc.) on Windows or Linux.  
- **AI-powered prompts**: Use `:ai <prompt>` to ask questions or get assistance from OpenRouter LLM.  
- **Contextual AI prompts**: Use `:ai -reply + <prompt>` to include the previous shell or AI output in your new prompt. Perfect for debugging or building on prior output.  
- **Persistent API key storage**: Saves your OpenRouter API key locally (`~/.ai_shell_config.json`) so you don’t need to enter it every time.  
- **Manage API key in REPL**:  
  - `:showkey` → View current API key (masked).  
  - `:setkey <new_key>` → Overwrite and save a new API key.  
- **Cross-platform**: Works on Windows and Linux (requires Python 3.10+).  
- **Threaded output streaming**: Live output for stdout and stderr of shell commands.  

---

## Requirements

- Python 3.10 or higher
- `requests` library  

**requirements.txt**:

```

requests>=2.31.0

````

Install dependencies via:

```bash
pip install -r requirements.txt
````

---

## Installation

1. Clone this repository or copy the Python script (`dmh_ai_shell.py`) to your machine.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the shell:

```bash
python dmh_ai_shell.py
```

4. On first run, you will be prompted to enter your **OpenRouter API Key**. This key will be saved in `~/.ai_shell_config.json` for future sessions.

---

## Usage

Once the shell starts, you will see the banner:

```
========================================
 🚀 DMH AI Shell with OpenRouter integration
 Commands:
   :ai <prompt>       → Ask the AI
   :ai -reply + <prompt> → Include last output in the new prompt
   :showkey           → Show current API key (masked)
   :setkey <key>      → Overwrite and save a new API key
   exit               → Quit
========================================
>
```

### Commands

| Command                 | Description                                                         |
| ----------------------- | ------------------------------------------------------------------- |
| `:ai <prompt>`          | Ask the AI model a question or request.                             |
| `:ai -reply + <prompt>` | Include previous output in the new AI prompt. Useful for debugging. |
| `:showkey`              | Display the currently saved API key (masked).                       |
| `:setkey <key>`         | Overwrite and save a new OpenRouter API key.                        |
| `exit`                  | Exit the DMH AI Shell.                                              |

### Examples

* **Run a shell command:**

```bash
> ls -lh
```

* **Ask AI for help:**

```bash
> :ai suggest a command to list the 5 largest files
[AI] You can use: `ls -lhS | head -n 5`
```

* **Ask AI with context of last output:**

```bash
> :ai -reply + How can I fix the error above?
[AI] Based on the previous output, it seems you are missing ...
```

* **View or update your API key:**

```bash
> :showkey
🔑 Current key: abcd********wxyz

> :setkey sk-newapikey123456
✅ API key updated.
```

---

## Notes

* The shell works on both **Windows** and **Linux**. On Windows, shell builtins like `dir` are supported.
* The previous output (for `:ai -reply +`) includes both **AI and shell responses**. This is useful for step-by-step debugging or explanations.
* API key is stored in your home directory in a file with restricted permissions (`~/.ai_shell_config.json`) for security.

---

## License

This project is open-source. You are free to use, modify, and distribute it for personal or commercial use.

---

## Acknowledgements

* [OpenRouter API](https://openrouter.ai/) for LLM integration.
* Inspired by AI-powered shells like “Cursor” and LLM-enhanced developer tools.

```

--
```
