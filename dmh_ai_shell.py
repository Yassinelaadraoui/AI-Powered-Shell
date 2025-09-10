import os
import json
import requests
import subprocess
import threading
import sys
import shlex
from pathlib import Path
import platform
from colorama import init, Fore, Style

# Initialize colorama (Windows)
init(autoreset=True)

CONFIG_FILE = Path.home() / ".ai_shell_config.json"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-4o-mini"


# -----------------------------
# Color output
# -----------------------------
def print_ai_box(text: str, model: str, color=Fore.CYAN):
    """
    Prints text inside a box with colored border for AI output.
    Includes model name in the first line.
    """
    # Add model info as first line
    model_line = f"Model: {model}"
    lines = [model_line, ""] + (text.splitlines() or [""])

    # Determine box width
    width = max(len(line) for line in lines)
    horizontal = "─" * (width + 2)

    print(color + "┌" + horizontal + "┐")
    for i, line in enumerate(lines):
        if i == 0:  # Model line - make it bold/highlighted
            print(color + "│ " + Style.BRIGHT + line.ljust(width) + " " + color + "│")
        else:
            print(color + "│ " + line.ljust(width) + " │")
    print(color + "└" + horizontal + "┘" + Style.RESET_ALL)


# -----------------------------
# CONFIG HANDLING
# -----------------------------
def load_config() -> dict:
    """Load configuration including API key and model preference."""
    config = {
        "OPENROUTER_API_KEY": "",
        "DEFAULT_MODEL": DEFAULT_MODEL
    }
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                saved_config = json.load(f)
                config.update(saved_config)
        except Exception:
            pass
    
    # If no API key, prompt for it
    if not config["OPENROUTER_API_KEY"]:
        api_key = input("🔑 Enter your OpenRouter API Key: ").strip()
        config["OPENROUTER_API_KEY"] = api_key
        save_config(config)
    
    return config


def save_config(config: dict):
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        try:
            os.chmod(CONFIG_FILE, 0o600)
        except Exception:
            pass
        print(f"✅ Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"⚠️ Failed to save configuration: {e}")


def save_api_key(key: str):
    """Legacy function - now uses save_config."""
    config = load_config()
    config["OPENROUTER_API_KEY"] = key
    save_config(config)


def mask_key(key: str) -> str:
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


# -----------------------------
# het the env of the system
# -----------------------------
def get_os():
    os_name = platform.system()
    if os_name == "Windows":
        return "Windows"
    elif os_name == "Linux":
        return "Linux"
    elif os_name == "Darwin":
        return "MacOS"
    else:
        return os_name


# -----------------------------
# OPENROUTER CALL
# -----------------------------
def call_openrouter(prompt: str, model: str, api_key: str) -> tuple[str, str]:
    """
    Send a prompt to OpenRouter API and return the AI reply and model used.
    Returns (response_text, model_used)
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
        
    user_os = get_os()

    SYSTEM_PROMPT = f"""
        You are DMH AI Shell Assistant, an expert command-line helper and AI shell assistant.
        The user is running {user_os}. You should ONLY suggest commands, syntax, and examples
        that work for {user_os}. 

        Rules:
        1. Always interpret the user's prompt in the context of the command-line environment.
        2. If given shell output, analyze it carefully and suggest practical next steps.
        3. When suggesting commands, always prioritize safety and avoid destructive actions.
        4. Explain errors clearly and provide concise examples or fixes when possible.
        5. Do not include irrelevant information; keep responses short but informative.
        6. When the user uses ':ai -reply +', consider the previous output as context.
        7. Assume the environment is {user_os}, and provide platform relevant solutions .
        8. Avoid guessing; only suggest commands or fixes that are likely to work.

        Your response format:
        - Short explanation (if applicable)
        - Command(s) or steps (if needed)
        - Optional notes for safety or context
        """

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        response_text = result["choices"][0]["message"]["content"]
        # Get the actual model used (in case of fallback)
        model_used = result.get("model", model)
        return response_text, model_used
    except Exception as e:
        return f"⚠️ Error calling OpenRouter: {e}", model



# -----------------------------
# print_creator_info CALL
# -----------------------------
def print_creator_info():
    """Display creator contact information in a nice format."""
    creator_info = """
👨‍💻 DMH AI Shell - Created by Yassine Laadraoui

📧 Email:    yassinelaadraoui@gmail.com
💼 LinkedIn: https://www.linkedin.com/in/yassinelaadraoui/
🐙 GitHub:   https://github.com/Yassinelaadraoui/AI-Powered-Shell

Feel free to reach out for questions, suggestions, or contributions!
    """
    
    lines = creator_info.strip().splitlines()
    width = max(len(line) for line in lines)
    horizontal = "─" * (width + 2)
    
    print(Fore.GREEN + "┌" + horizontal + "┐")
    for line in lines:
        print(Fore.GREEN + "│ " + line.ljust(width) + " │")
    print(Fore.GREEN + "└" + horizontal + "┘" + Style.RESET_ALL)


# -----------------------------
# MODEL PARSING
# -----------------------------
def parse_ai_command(command: str) -> tuple[str, str]:
    """
    Parse AI command to extract model and prompt.
    Returns (model, prompt) where model is None if not specified.
    
    Examples:
    ":ai how to list files" -> (None, "how to list files")
    ":ai -m openai/gpt-4 how to list files" -> ("openai/gpt-4", "how to list files")
    ":ai -model claude-3-sonnet how to list files" -> ("claude-3-sonnet", "how to list files")
    """
    parts = command.split()
    
    if len(parts) < 2:
        return None, ""
    
    # Check for model flags
    if parts[0] in ["-m", "-model"]:
        if len(parts) < 3:
            return None, ""
        model = parts[1]
        prompt = " ".join(parts[2:])
        return model, prompt
    elif len(parts) >= 3 and parts[0] in ["-m", "-model"]:
        model = parts[1]
        prompt = " ".join(parts[2:])
        return model, prompt
    else:
        # No model specified
        prompt = " ".join(parts)
        return None, prompt


# -----------------------------
# SHELL COMMAND EXECUTION
# -----------------------------
def stream_reader(pipe, target, output_list):
    """
    Read lines from a subprocess pipe and write to target (stdout/stderr),
    also append to output_list to capture last output.
    """
    for line in iter(pipe.readline, b''):
        try:
            decoded = line.decode(errors='replace')
            target.write(decoded)
            output_list.append(decoded)
        except Exception:
            target.write(line)
        target.flush()
    pipe.close()


def run_command(cmd) -> str:
    """
    Execute shell command and capture output.
    Returns combined stdout + stderr as a string.
    """
    use_shell = False if isinstance(cmd, (list,)) else True if sys.platform == 'win32' else False
    if isinstance(cmd, str) and not use_shell:
        cmd = shlex.split(cmd)

    p = subprocess.Popen(cmd,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=use_shell)

    output_list = []
    t1 = threading.Thread(target=stream_reader, args=(p.stdout, sys.stdout, output_list))
    t2 = threading.Thread(target=stream_reader, args=(p.stderr, sys.stderr, output_list))
    t1.start(); t2.start()
    p.wait()
    t1.join(); t2.join()
    return "".join(output_list)  # return full captured output


# -----------------------------
# REPL LOOP
# -----------------------------
def repl():
    """
    Main REPL loop.
    Tracks last output (shell or AI) for context when using ':ai -reply +'.
    """
    config = load_config()
    last_output = ""  # stores the last output for reference

    print("="*50)
    print(" 🚀 DMH AI Shell with OpenRouter integration ")
    print(" Commands:")
    print("   :ai <prompt>                    → Ask the AI (use default model)")
    print("   :ai -m <model> <prompt>         → Ask AI with specific model")
    print("   :ai -model <model> <prompt>     → Ask AI with specific model (alternative)")
    print("   :ai -reply + <prompt>           → Include last output in prompt")
    print("   :ai -m <model> -reply + <prompt> → Specific model + last output")
    print("   :showkey                        → Show current API key (masked)")
    print("   :setkey <key>                   → Set new API key")
    print("   :showmodel                      → Show current default model")
    print("   :setmodel <model>               → Set new default model")
    print("   :creator                        → Show creator contact information")
    print("   exit                            → Quit")
    print("="*50)
    print(f"Current default model: {config['DEFAULT_MODEL']}")
    print()

    while True:
        try:
            line = input("> ")
        except EOFError:
            break
        if not line:
            continue
        if line.strip() == "exit":
            break

        # Handle AI commands with -reply + flag
        if ":ai" in line and "-reply +" in line:
            # Extract everything after ":ai "
            ai_part = line[line.find(":ai") + 4:].strip()
            
            # Check if there's a model specified before -reply +
            if ai_part.startswith(("-m ", "-model ")):
                # Parse model from the beginning
                parts = ai_part.split()
                if len(parts) >= 4 and "-reply" in parts and "+" in parts:
                    model_flag = parts[0]  # -m or -model
                    specified_model = parts[1]
                    
                    # Find -reply + and get everything after
                    try:
                        reply_idx = next(i for i, p in enumerate(parts) if p == "-reply")
                        if reply_idx + 1 < len(parts) and parts[reply_idx + 1] == "+":
                            user_prompt = " ".join(parts[reply_idx + 2:])
                        else:
                            user_prompt = " ".join(parts[reply_idx + 1:])
                    except StopIteration:
                        user_prompt = ""
                else:
                    specified_model = config['DEFAULT_MODEL']
                    user_prompt = ai_part.replace("-reply +", "").strip()
            else:
                # No model specified, use default
                specified_model = config['DEFAULT_MODEL']
                user_prompt = ai_part.replace("-reply +", "").strip()
            
            combined_prompt = f"Previous output:\n{last_output}\n\nNew prompt:\n{user_prompt}"
            reply, model_used = call_openrouter(combined_prompt, specified_model, config['OPENROUTER_API_KEY'])
            print_ai_box(reply, model_used, color=Fore.CYAN)
            last_output = reply
            continue

        # Regular AI commands
        if line.startswith(":ai "):
            ai_command = line[4:].strip()  # Remove ":ai "
            specified_model, prompt = parse_ai_command(ai_command)
            
            # Use specified model or fall back to default
            model_to_use = specified_model or config['DEFAULT_MODEL']
            
            if not prompt.strip():
                print("⚠️ No prompt provided.")
                continue
                
            reply, model_used = call_openrouter(prompt, model_to_use, config['OPENROUTER_API_KEY'])
            print_ai_box(reply, model_used, color=Fore.CYAN)
            last_output = reply
            continue

        # Show current API key
        if line.strip() == ":showkey":
            print("🔑 Current key:", mask_key(config['OPENROUTER_API_KEY']))
            continue

        # Set new API key
        if line.startswith(":setkey "):
            new_key = line[len(":setkey "):].strip()
            if new_key:
                config['OPENROUTER_API_KEY'] = new_key
                save_config(config)
                print("✅ API key updated.")
            else:
                print("⚠️ No key provided.")
            continue

        # Show current default model
        if line.strip() == ":showmodel":
            print(f"🤖 Current default model: {config['DEFAULT_MODEL']}")
            continue

        # Set new default model
        if line.startswith(":setmodel "):
            new_model = line[len(":setmodel "):].strip()
            if new_model:
                config['DEFAULT_MODEL'] = new_model
                save_config(config)
                print(f"✅ Default model updated to: {new_model}")
            else:
                print("⚠️ No model provided.")
            continue

        # Show creator contact information
        if line.strip() == ":creator":
            print_creator_info()
            continue

        # Run shell command and capture output
        output = run_command(line)
        last_output = output  # save last output for possible ':ai -reply +' usage
        print(f"[exit code: {0 if output else 0}]")  # dummy exit code print


# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    repl()