import os
import json
import requests
import subprocess
import threading
import sys
import shlex
from pathlib import Path

CONFIG_FILE = Path.home() / ".ai_shell_config.json"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# -----------------------------
# API KEY HANDLING
# -----------------------------
def load_api_key() -> str:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                if "OPENROUTER_API_KEY" in data:
                    return data["OPENROUTER_API_KEY"]
        except Exception:
            pass
    api_key = input("🔑 Enter your OpenRouter API Key: ").strip()
    save_api_key(api_key)
    return api_key


def save_api_key(key: str):
    data = {"OPENROUTER_API_KEY": key}
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)
        try:
            os.chmod(CONFIG_FILE, 0o600)
        except Exception:
            pass
        print(f"✅ API key saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"⚠️ Failed to save API key: {e}")


def mask_key(key: str) -> str:
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


OPENROUTER_API_KEY = load_api_key()


# -----------------------------
# OPENROUTER CALL
# -----------------------------
def call_openrouter(prompt: str) -> str:
    """
    Send a prompt to OpenRouter API and return the AI reply.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an AI shell assistant."},
            {"role": "user", "content": prompt}
        ],
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error calling OpenRouter: {e}"


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
    global OPENROUTER_API_KEY

    last_output = ""  # stores the last output for reference

    print("="*40)
    print(" 🚀 DMH AI Shell with OpenRouter integration ")
    print(" Commands:")
    print("   :ai <prompt>       → Ask the AI")
    print("   :ai -reply + <prompt> → Include last output in the new prompt")
    print("   :showkey           → Show current API key (masked)")
    print("   :setkey <key>      → Overwrite and save a new API key")
    print("   exit               → Quit")
    print("="*40)

    while True:
        try:
            line = input("> ")
        except EOFError:
            break
        if not line:
            continue
        if line.strip() == "exit":
            break

        # AI prompt with last output included
        if line.startswith(":ai -reply + "):
            user_prompt = line[len(":ai -reply + "):]
            combined_prompt = f"Previous output:\n{last_output}\n\nNew prompt:\n{user_prompt}"
            reply = call_openrouter(combined_prompt)
            print(f"[AI] {reply}")
            last_output = reply  # update last output with AI response
            continue

        # Regular AI prompt
        if line.startswith(":ai "):
            prompt = line[len(":ai "):]
            reply = call_openrouter(prompt)
            print(f"[AI] {reply}")
            last_output = reply  # update last output
            continue

        # Show current API key
        if line.strip() == ":showkey":
            print("🔑 Current key:", mask_key(OPENROUTER_API_KEY))
            continue

        # Set new API key
        if line.startswith(":setkey "):
            new_key = line[len(":setkey "):].strip()
            if new_key:
                save_api_key(new_key)
                OPENROUTER_API_KEY = new_key
                print("✅ API key updated.")
            else:
                print("⚠️ No key provided.")
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
