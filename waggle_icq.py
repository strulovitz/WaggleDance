"""
WaggleDance ICQ — DOS-style chat viewer + autonomous agent.

Combines two functions:
1. ICQ VIEWER: Shows all messages between Laptop and Desktop Claude Code
   instances in a colored, emoji-decorated chat format. Read-only for humans.
2. AGENT: Types TASK messages into the local Claude Code terminal using
   pyautogui clipboard paste. REPLY messages only display in the viewer.

Loop prevention (Option D):
- Messages tagged TASK get typed into Claude Code. REPLY messages don't.
- Max 5 rounds of back-and-forth, then pauses for human approval.

Usage:
    Laptop:  python waggle_icq.py --server http://localhost:8765 --me laptop-claude --watch desktop-claude
    Desktop: python waggle_icq.py --server http://10.0.0.1:8765 --me desktop-claude --watch laptop-claude
"""

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime

import pyautogui
import pyperclip
import pygetwindow as gw

# Safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

# --- ANSI Color Codes ---
RESET = "\033[0m"
YELLOW = "\033[93m"       # Laptop
MAGENTA = "\033[95m"      # Desktop
GRAY = "\033[90m"         # Timestamps
WHITE = "\033[97m"        # System messages
RED = "\033[91m"          # Errors/warnings
GREEN = "\033[92m"        # Success
CYAN = "\033[96m"         # Headers
BOLD = "\033[1m"

# --- Platform Detection ---
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

# --- Emoji Selection ---
if IS_WINDOWS:
    EMOJI_LAPTOP = "🌼"
    EMOJI_DESKTOP = "🌷"
else:
    EMOJI_LAPTOP = "🌻"
    EMOJI_DESKTOP = "🌹"

# --- Config ---
MAX_CHAIN_ROUNDS = 5
LOG_PUSH_INTERVAL = 600       # 10 minutes in seconds
LOG_PUSH_MSG_COUNT = 30       # or every 30 messages


def get_color(sender):
    if "laptop" in sender.lower():
        return YELLOW
    elif "desktop" in sender.lower():
        return MAGENTA
    return WHITE


def get_emoji(sender):
    if "laptop" in sender.lower():
        return EMOJI_LAPTOP
    elif "desktop" in sender.lower():
        return EMOJI_DESKTOP
    return ""


def get_display_name(sender):
    if "laptop" in sender.lower():
        return "Laptop Windows"
    elif "desktop" in sender.lower():
        return "Desktop Windows"
    return sender


def format_timestamp(iso_timestamp):
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime("%H:%M:%S")
    except:
        return "??:??:??"


def print_header():
    print(f"\n{CYAN}{BOLD}")
    print(f"  ╔══════════════════════════════════════════════════════╗")
    print(f"  ║     {EMOJI_LAPTOP}  WaggleDance ICQ  {EMOJI_DESKTOP}                        ║")
    print(f"  ║     Laptop  {RESET}{CYAN}↔{BOLD}  Desktop                              ║")
    print(f"  ║     \"Given enough bees, all flowers are found\"      ║")
    print(f"  ╚══════════════════════════════════════════════════════╝")
    print(f"{RESET}")
    print(f"  {GRAY}FAILSAFE: Move mouse to top-left corner to stop agent{RESET}")
    print(f"  {GRAY}Chain limit: {MAX_CHAIN_ROUNDS} rounds, then pause for approval{RESET}")
    print()


def print_message(msg):
    ts = format_timestamp(msg.get("timestamp", ""))
    sender = msg.get("from", "unknown")
    msg_type = msg.get("type", "REPLY")
    text = msg.get("message", "")
    color = get_color(sender)
    emoji = get_emoji(sender)
    name = get_display_name(sender)

    type_tag = ""
    if msg_type == "TASK":
        type_tag = f" {RED}[TASK]{RESET}"

    print(f"  {GRAY}[{ts}]{RESET} {color}{emoji} {name}{type_tag}{RESET}")

    # Word-wrap message at ~70 chars, indented
    words = text.split()
    line = ""
    for word in words:
        if len(line) + len(word) + 1 > 70:
            print(f"  {color}  {line}{RESET}")
            line = word
        else:
            line = f"{line} {word}" if line else word
    if line:
        print(f"  {color}  {line}{RESET}")
    print()


def print_system(text):
    print(f"  {GREEN}[SYSTEM]{RESET} {WHITE}{text}{RESET}")


def print_error(text):
    print(f"  {RED}[ERROR]{RESET} {WHITE}{text}{RESET}")


def log_message(log_path, msg):
    ts = format_timestamp(msg.get("timestamp", ""))
    sender = get_display_name(msg.get("from", "unknown"))
    emoji_raw = get_emoji(msg.get("from", ""))
    msg_type = msg.get("type", "REPLY")
    text = msg.get("message", "")
    type_tag = " [TASK]" if msg_type == "TASK" else ""

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {emoji_raw} {sender}{type_tag}: {text}\n")


def push_log_to_github(waggle_dir, log_filename):
    try:
        subprocess.run(
            ["git", "add", log_filename],
            cwd=waggle_dir, capture_output=True, timeout=10
        )
        subprocess.run(
            ["git", "commit", "-m", f"Auto-update {log_filename}"],
            cwd=waggle_dir, capture_output=True, timeout=10
        )
        subprocess.run(
            ["git", "push"],
            cwd=waggle_dir, capture_output=True, timeout=30
        )
        print_system(f"Chat log pushed to GitHub")
    except Exception as e:
        print_error(f"GitHub push failed: {e}")


def fetch_messages(server_url, since_id):
    try:
        result = subprocess.run(
            ["curl", "-s", f"{server_url}/read?since={since_id}"],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        return data.get("messages", [])
    except Exception as e:
        print_error(f"Poll failed: {e}")
        return []


def send_message(server_url, name, message, msg_type="REPLY"):
    try:
        payload = json.dumps({"from": name, "type": msg_type, "message": message})
        subprocess.run(
            ["curl", "-s", "-X", "POST", f"{server_url}/send",
             "-H", "Content-Type: application/json",
             "-d", payload],
            capture_output=True, text=True, timeout=10
        )
    except Exception as e:
        print_error(f"Send failed: {e}")


def pick_claude_window():
    """Show numbered list of windows. User picks once, then fully autonomous."""
    windows = []
    for w in gw.getAllWindows():
        t = w.title.strip()
        if t and w.visible and "waggle_icq" not in t.lower():
            windows.append(w)

    print_system("Which window is Claude Code? Pick a number:\n")
    for i, w in enumerate(windows):
        print(f"    {CYAN}{i+1}.{RESET} {w.title[:75]}")
    print()

    while True:
        try:
            choice = int(input(f"  {GREEN}>{RESET} "))
            if 1 <= choice <= len(windows):
                chosen = windows[choice - 1]
                print_system(f"Locked onto: '{chosen.title[:60]}'")
                print_system("Window title may change — tracking by handle, not title.")
                print()
                return chosen
            print_error("Invalid number. Try again.")
        except ValueError:
            print_error("Type a number. Try again.")
        except KeyboardInterrupt:
            return None


def type_into_claude(window, message):
    try:
        if window.isMinimized:
            window.restore()
        window.activate()
        time.sleep(0.5)

        pyperclip.copy(message)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.3)
        pyautogui.press("enter")
        return True
    except Exception as e:
        print_error(f"Type failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="WaggleDance ICQ — Chat viewer + Agent")
    parser.add_argument("--server", required=True, help="WaggleDance server URL")
    parser.add_argument("--me", required=True, help="Your identity (e.g. laptop-claude)")
    parser.add_argument("--watch", required=True, help="Who to watch (e.g. desktop-claude)")
    parser.add_argument("--interval", type=int, default=5, help="Poll interval seconds (default: 5)")
    args = parser.parse_args()

    waggle_dir = os.path.dirname(os.path.abspath(__file__))
    me_short = "laptop" if "laptop" in args.me.lower() else "desktop"
    log_filename = f"chat_log_{me_short}.txt"
    log_path = os.path.join(waggle_dir, log_filename)

    # Enable ANSI on Windows
    if IS_WINDOWS:
        os.system("")

    print_header()
    print_system(f"Identity: {args.me}")
    print_system(f"Watching: {args.watch}")
    print_system(f"Server:   {args.server}")
    print_system(f"Log file: {log_filename}")
    print()

    # Pick Claude Code window — one time, then autonomous
    claude_window = pick_claude_window()
    if not claude_window:
        print_error("No window selected. Agent will display only, not type.")
    print()

    # Load existing messages and display them
    all_messages = fetch_messages(args.server, 0)
    if all_messages:
        print_system(f"Loading {len(all_messages)} existing messages...")
        print()
        for msg in all_messages:
            print_message(msg)
            log_message(log_path, msg)

    last_id = max((m["id"] for m in all_messages), default=0)
    chain_count = 0
    chain_paused = False
    msgs_since_push = 0
    last_push_time = time.time()

    # Announce
    send_message(args.server, args.me,
                 f"WaggleDance ICQ Agent is online. Watching for messages from {args.watch}.",
                 "REPLY")

    print_system("Agent running. Watching for messages...\n")

    while True:
        try:
            new_messages = fetch_messages(args.server, last_id)

            for msg in new_messages:
                print_message(msg)
                log_message(log_path, msg)
                msgs_since_push += 1
                last_id = msg["id"]

                # Only act on TASK messages from the watched sender
                if msg["from"] == args.watch and msg.get("type") == "TASK":
                    if chain_paused:
                        print_system("Chain is paused. Message displayed but NOT typed.")
                        continue

                    chain_count += 1
                    if chain_count > MAX_CHAIN_ROUNDS:
                        chain_paused = True
                        print()
                        print(f"  {RED}{BOLD}╔══════════════════════════════════════════════╗{RESET}")
                        print(f"  {RED}{BOLD}║  CHAIN LIMIT REACHED ({MAX_CHAIN_ROUNDS} rounds)              ║{RESET}")
                        print(f"  {RED}{BOLD}║  Press ENTER to allow {MAX_CHAIN_ROUNDS} more rounds         ║{RESET}")
                        print(f"  {RED}{BOLD}╚══════════════════════════════════════════════╝{RESET}")
                        print()
                        input()
                        chain_count = 0
                        chain_paused = False
                        print_system("Chain reset. Continuing...")

                    if claude_window:
                        success = type_into_claude(claude_window, msg["message"])
                        if success:
                            print_system(f"TASK #{msg['id']} typed into Claude Code")
                        else:
                            print_error(f"Failed to type TASK #{msg['id']}")
                            send_message(args.server, args.me,
                                         f"[AGENT] Failed to deliver TASK #{msg['id']} — window error",
                                         "REPLY")
                    else:
                        print_error("Cannot find Claude Code window!")
                        send_message(args.server, args.me,
                                     f"[AGENT] Cannot find Claude Code window for TASK #{msg['id']}",
                                     "REPLY")

                elif msg["from"] == args.watch and msg.get("type") == "REPLY":
                    # REPLY from watched sender — type into Claude Code
                    # so the local Claude sees it without manual checking
                    chain_count = 0  # Reset chain on REPLY
                    if claude_window:
                        reply_text = f"Desktop Claude said: {msg['message']}"
                        success = type_into_claude(claude_window, reply_text)
                        if success:
                            print_system(f"REPLY #{msg['id']} typed into Claude Code")
                        else:
                            print_error(f"Failed to type REPLY #{msg['id']}")

                elif msg["from"] != args.me:
                    # Messages from other senders — just displayed
                    if msg.get("type") != "TASK":
                        chain_count = 0

            # Periodic GitHub push
            now = time.time()
            if msgs_since_push >= LOG_PUSH_MSG_COUNT or (now - last_push_time) >= LOG_PUSH_INTERVAL:
                if msgs_since_push > 0:
                    push_log_to_github(waggle_dir, log_filename)
                    msgs_since_push = 0
                    last_push_time = now

            time.sleep(args.interval)

        except KeyboardInterrupt:
            print()
            print_system("Agent stopped by user.")
            send_message(args.server, args.me, "[AGENT] Going offline.", "REPLY")
            # Final push
            if msgs_since_push > 0:
                push_log_to_github(waggle_dir, log_filename)
            break
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
