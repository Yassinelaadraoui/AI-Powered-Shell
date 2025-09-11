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
    model_line = f"Model: {model}"
    lines = [model_line, ""] + (text.splitlines() or [""])
    width = max(len(line) for line in lines)
    horizontal = "─" * (width + 2)
    print(color + "┌" + horizontal + "┐")
    for i, line in enumerate(lines):
        if i == 0:
            print(color + "│ " + Style.BRIGHT + line.ljust(width) + " " + color + "│")
        else:
            print(color + "│ " + line.ljust(width) + " │")
    print(color + "└" + horizontal + "┘" + Style.RESET_ALL)

# -----------------------------
# CONFIG HANDLING
# -----------------------------
def load_config() -> dict:
    config = {"OPENROUTER_API_KEY": "", "DEFAULT_MODEL": DEFAULT_MODEL}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                saved_config = json.load(f)
                config.update(saved_config)
        except Exception:
            pass
    if not config["OPENROUTER_API_KEY"]:
        api_key = input("🔑 Enter your OpenRouter API Key: ").strip()
        config["OPENROUTER_API_KEY"] = api_key
        save_config(config)
    return config

def save_config(config: dict):
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

def mask_key(key: str) -> str:
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]

# -----------------------------
# get the env of the system
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
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    user_os = get_os()

    SYSTEM_PROMPT = f"""
    You are DMH AI Shell Assistant, an expert cross-platform command-line helper.
    The user is running {user_os}. Only suggest commands that work for {user_os}.

    You MUST always reply in the following strict format:

    COMMAND:
    <the exact command(s) to run>

    EXPLANATION:
    <clear plain English explanation of what the command does>

    SAFE:
    <✅ if safe, or ⚠️ with reason if destructive>

    Rules:
    1. Convert natural language into shell commands.
    2. If multiple steps are needed, output them in COMMAND with line breaks.
    3. Use {user_os}-specific syntax.
    4. Warn ⚠️ if the command is destructive (delete, kill, overwrite).
    5. Never output anything outside the structured format.
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
        model_used = result.get("model", model)
        return response_text, model_used
    except Exception as e:
        return f"⚠️ Error calling OpenRouter: {e}", model

# -----------------------------
# CREATOR INFO
# -----------------------------
def print_creator_info():
    creator_info = """
👨‍💻 DMH AI Shell - Created by Yassine Laadraoui

📧 Email:    yassinelaadraoui@gmail.com
💼 LinkedIn: https://www.linkedin.com/in/yassinelaadraoui/
🐙 GitHub:   https://github.com/Yassinelaadraoui/AI-Powered-Shell
"""
    lines = creator_info.strip().splitlines()
    width = max(len(line) for line in lines)
    horizontal = "─" * (width + 2)
    print(Fore.GREEN + "┌" + horizontal + "┐")
    for line in lines:
        print(Fore.GREEN + "│ " + line.ljust(width) + " │")
    print(Fore.GREEN + "└" + horizontal + "┘" + Style.RESET_ALL)

# -----------------------------
# AI RESPONSE PARSER
# -----------------------------
def parse_ai_response(reply: str):
    command, explanation, safe = "", "", "✅"
    if "COMMAND:" in reply:
        command = reply.split("COMMAND:", 1)[1].split("EXPLANATION:")[0].strip()
    if "EXPLANATION:" in reply:
        explanation = reply.split("EXPLANATION:", 1)[1].split("SAFE:")[0].strip()
    if "SAFE:" in reply:
        safe = reply.split("SAFE:", 1)[1].strip()
    return command, explanation, safe

# -----------------------------
# SHELL COMMAND EXECUTION
# -----------------------------
def stream_reader(pipe, target, output_list):
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
    use_shell = False if isinstance(cmd, (list,)) else True if sys.platform == 'win32' else False
    if isinstance(cmd, str) and not use_shell:
        cmd = shlex.split(cmd)
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=use_shell)
    output_list = []
    t1 = threading.Thread(target=stream_reader, args=(p.stdout, sys.stdout, output_list))
    t2 = threading.Thread(target=stream_reader, args=(p.stderr, sys.stderr, output_list))
    t1.start(); t2.start()
    p.wait()
    t1.join(); t2.join()
    return "".join(output_list)

# -----------------------------
# REPL LOOP
# -----------------------------
def repl():
    config = load_config()
    last_output = ""

    print("="*50)
    print(" 🚀 DMH AI Shell with OpenRouter integration ")
    print(" Commands:")
    print("   :ai <prompt>                    → Ask the AI (use default model)")
    print("   :ai -m <model> <prompt>         → Ask AI with specific model")
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

        # Handle commands starting with :ai
        if line.startswith(":ai"):
            ai_command = line[3:].strip()
            model_to_use = config['DEFAULT_MODEL']
            prompt = ai_command
            reply, model_used = call_openrouter(prompt, model_to_use, config['OPENROUTER_API_KEY'])
            command, explanation, safe = parse_ai_response(reply)

            print_ai_box(f"COMMAND:\n{command}\n\nEXPLANATION:\n{explanation}\n\nSAFE:\n{safe}", model_used)
            if command:
                if safe.startswith("⚠️"):
                    confirm = input(f"{safe}\nRun anyway? (y/N): ").lower()
                    if confirm != "y":
                        print("❌ Command aborted.")
                        continue
                print(f"⚙️ Running: {command}")
                run_command(command)
            last_output = reply
            continue

        # Built-in commands
        if line.strip() == ":showkey":
            print("🔑 Current key:", mask_key(config['OPENROUTER_API_KEY']))
            continue
        if line.startswith(":setkey "):
            new_key = line[len(":setkey "):].strip()
            if new_key:
                config['OPENROUTER_API_KEY'] = new_key
                save_config(config)
                print("✅ API key updated.")
            continue
        if line.strip() == ":showmodel":
            print(f"🤖 Current default model: {config['DEFAULT_MODEL']}")
            continue
        if line.startswith(":setmodel "):
            new_model = line[len(":setmodel "):].strip()
            if new_model:
                config['DEFAULT_MODEL'] = new_model
                save_config(config)
                print(f"✅ Default model updated to: {new_model}")
            continue
        if line.strip() == ":creator":
            print_creator_info()
            continue

        import shutil

        # Decide: AI or shell
        first_word = line.split()[0]
        if shutil.which(first_word):
            # Valid shell command → run normally
            output = run_command(line)
            last_output = output
            print(f"[exit code: {0 if output else 0}]")
        else:
            # Not a known command → send to AI
            print("🤖 Sending to AI...")
            reply, model_used = call_openrouter(line, config['DEFAULT_MODEL'], config['OPENROUTER_API_KEY'])
            command, explanation, safe = parse_ai_response(reply)
            print_ai_box(f"COMMAND:\\n{command}\\n\\nEXPLANATION:\\n{explanation}\\n\\nSAFE:\\n{safe}", model_used)
            if command:
                if safe.startswith("⚠️"):
                    confirm = input(f"{safe}\\nRun anyway? (y/N): ").lower()
                    if confirm != "y":
                        print("❌ Command aborted.")
                        continue
                print(f"⚙️ Running: {command}")
                run_command(command)
            last_output = reply

# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    repl()
