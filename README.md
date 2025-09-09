# DMH AI Shell with OpenRouter Integration

🚀 **DMH AI Shell** is a Python-based interactive shell wrapper that integrates with the **OpenRouter API** to provide AI-powered assistance. It allows you to execute normal shell commands while also querying an LLM for explanations, suggestions, and debugging with support for custom model selection.

---

## Features

- **Interactive shell**: Execute standard shell commands (`ls`, `dir`, `ping`, etc.) on Windows, macOS, or Linux.  
- **AI-powered prompts**: Use `:ai <prompt>` to ask questions or get assistance from OpenRouter LLM.  
- **Custom model selection**: Choose specific models for each query or set a default model preference.
- **Model display**: Each AI response clearly shows which model was used to generate the response.
- **Contextual AI prompts**: Use `:ai -reply + <prompt>` to include the previous shell or AI output in your new prompt. Perfect for debugging or building on prior output.  
- **Persistent configuration**: Saves your OpenRouter API key and default model locally (`~/.ai_shell_config.json`) so you don't need to enter them every time.  
- **Complete configuration management**:  
  - `:showkey` → View current API key (masked).  
  - `:setkey <new_key>` → Overwrite and save a new API key.
  - `:showmodel` → View current default model.
  - `:setmodel <model>` → Set new default model.
- **Cross-platform**: Works on Windows, macOS, and Linux (requires Python 3.10+).  
- **Threaded output streaming**: Live output for stdout and stderr of shell commands.  
- **Colored output**: Beautiful boxed AI responses with color-coded borders.

---

## Requirements

- Python 3.10 or higher
- `requests` library  
- `colorama` library (for colored output)

**requirements.txt**:

```
requests>=2.31.0
colorama>=0.4.6
```

Install dependencies via:

```bash
pip install -r requirements.txt
```

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
==================================================
 🚀 DMH AI Shell with OpenRouter integration 
 Commands:
   :ai <prompt>                    → Ask the AI (use default model)
   :ai -m <model> <prompt>         → Ask AI with specific model
   :ai -model <model> <prompt>     → Ask AI with specific model (alternative)
   :ai -reply + <prompt>           → Include last output in prompt
   :ai -m <model> -reply + <prompt> → Specific model + last output
   :showkey                        → Show current API key (masked)
   :setkey <key>                   → Set new API key
   :showmodel                      → Show current default model
   :setmodel <model>               → Set new default model
   exit                            → Quit
==================================================
Current default model: openai/gpt-4o-mini

>
```

### Commands

| Command                              | Description                                                         |
| ------------------------------------ | ------------------------------------------------------------------- |
| `:ai <prompt>`                       | Ask the AI model a question using the default model.               |
| `:ai -m <model> <prompt>`            | Ask AI with a specific model (short form).                         |
| `:ai -model <model> <prompt>`        | Ask AI with a specific model (long form).                          |
| `:ai -reply + <prompt>`              | Include previous output in the new AI prompt. Useful for debugging.|
| `:ai -m <model> -reply + <prompt>`   | Use specific model and include previous output.                     |
| `:showkey`                           | Display the currently saved API key (masked).                      |
| `:setkey <key>`                      | Overwrite and save a new OpenRouter API key.                       |
| `:showmodel`                         | Display the current default model.                                 |
| `:setmodel <model>`                  | Set a new default model for future AI queries.                     |
| `exit`                               | Exit the DMH AI Shell.                                             |

### Examples

**Run a shell command:**
```bash
> ls -lh
```

**Ask AI for help (using default model):**
```bash
> :ai suggest a command to list the 5 largest files
┌─────────────────────────────────────────────────────┐
│ Model: openai/gpt-4o-mini                           │
│                                                     │
│ You can use: `ls -lhS | head -n 5`                  │
│ This sorts files by size (largest first) and       │
│ shows the top 5.                                    │
└─────────────────────────────────────────────────────┘
```

**Ask AI with a specific model:**
```bash
> :ai -m anthropic/claude-3-sonnet explain how grep works
┌─────────────────────────────────────────────────────┐
│ Model: anthropic/claude-3-sonnet                    │
│                                                     │
│ grep is a command-line utility that searches for   │
│ patterns in text files using regular expressions...│
└─────────────────────────────────────────────────────┘
```

**Ask AI with context of last output:**
```bash
> :ai -reply + How can I fix the error above?
┌─────────────────────────────────────────────────────┐
│ Model: openai/gpt-4o-mini                           │
│                                                     │
│ Based on the previous output, it seems you are      │
│ missing the required permissions. Try using sudo... │
└─────────────────────────────────────────────────────┘
```

**Use specific model with previous output:**
```bash
> :ai -m anthropic/claude-3-opus -reply + provide a detailed analysis of this error
```

**Manage your configuration:**
```bash
> :showkey
🔑 Current key: abcd********wxyz

> :setkey sk-newapikey123456
✅ API key updated.

> :showmodel
🤖 Current default model: openai/gpt-4o-mini

> :setmodel anthropic/claude-3-sonnet
✅ Default model updated to: anthropic/claude-3-sonnet
```

---

## Supported Models

DMH AI Shell supports any model available through OpenRouter. Popular options include:

**OpenAI Models:**
- `openai/gpt-4o` - Latest GPT-4 model
- `openai/gpt-4o-mini` - Faster, cost-effective GPT-4
- `openai/gpt-4-turbo` - GPT-4 Turbo
- `openai/gpt-3.5-turbo` - GPT-3.5 Turbo

**Anthropic Models:**
- `anthropic/claude-3-opus` - Most capable Claude model
- `anthropic/claude-3-sonnet` - Balanced performance and speed
- `anthropic/claude-3-haiku` - Fastest Claude model

**Google Models:**
- `google/gemini-pro` - Google's Gemini Pro
- `google/palm-2` - Google's PaLM 2

**Other Models:**
- `meta-llama/llama-2-70b-chat` - Meta's Llama 2
- `mistralai/mixtral-8x7b-instruct` - Mixtral model
- `cohere/command` - Cohere's Command model

For the complete list of available models, visit [OpenRouter's model list](https://openrouter.ai/models).

---

## Configuration

The configuration file (`~/.ai_shell_config.json`) stores:

```json
{
  "OPENROUTER_API_KEY": "your-api-key-here",
  "DEFAULT_MODEL": "openai/gpt-4o-mini"
}
```

This file is created with restricted permissions (600) for security.

---

## Notes

- The shell works on **Windows**, **macOS**, and **Linux**. On Windows, shell builtins like `dir` are supported.
- The previous output (for `:ai -reply +`) includes both **AI and shell responses**. This is useful for step-by-step debugging or explanations.
- Each AI response displays the model used, including cases where OpenRouter falls back to a different model.
- Model names must match those available on OpenRouter. Invalid models will result in API errors.
- The system automatically detects your operating system and provides OS-appropriate command suggestions.

---

## License

This project is open-source. You are free to use, modify, and distribute it for personal or commercial use.

---

## Acknowledgements

- [OpenRouter API](https://openrouter.ai/) for LLM integration.
- [Colorama](https://pypi.org/project/colorama/) for cross-platform colored terminal output.
- Inspired by AI-powered shells like "Cursor" and LLM-enhanced developer tools.