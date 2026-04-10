"""
WaggleDance Agent — Autonomous bridge between two Claude Code instances.

Runs in background on the REMOTE machine (the one that doesn't host the server).
Polls the WaggleDance server for new messages and types them into the local
Claude Code terminal as if the user were typing.

Same session. Same context. No extra tokens. Just a robot pretending to be you.

Usage:
    python waggle_agent.py --server http://10.0.0.1:8765 --name desktop-claude --watch laptop-claude
"""

import argparse
import time
import json
import subprocess
import pyautogui
import pyperclip
import pygetwindow as gw

# Safety: don't let pyautogui go haywire
pyautogui.FAILSAFE = True  # Move mouse to top-left corner to abort
pyautogui.PAUSE = 0.05


def find_claude_window():
    """Find the terminal window running Claude Code."""
    for w in gw.getAllWindows():
        title = w.title.lower()
        # Claude Code runs in terminal windows — look for common patterns
        if any(keyword in title for keyword in ['claude', 'terminal', 'cmd', 'powershell', 'bash', 'mintty', 'windows terminal']):
            # Skip our own window if we're running in a terminal too
            if 'waggle_agent' not in title:
                return w
    return None


def get_new_messages(server_url, since_id, watch_name):
    """Poll WaggleDance for new messages from the watched sender."""
    try:
        result = subprocess.run(
            ['curl', '-s', f'{server_url}/read?since={since_id}'],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        return [m for m in data['messages'] if m['from'] == watch_name]
    except Exception as e:
        print(f"[poll error] {e}")
        return []


def send_reply(server_url, name, message):
    """Send a reply back to WaggleDance."""
    try:
        payload = json.dumps({"from": name, "message": message})
        subprocess.run(
            ['curl', '-s', '-X', 'POST', f'{server_url}/send',
             '-H', 'Content-Type: application/json',
             '-d', payload],
            capture_output=True, text=True, timeout=10
        )
    except Exception as e:
        print(f"[send error] {e}")


def type_into_claude(window, message):
    """Focus the Claude Code window and type the message."""
    try:
        # Activate the window
        if window.isMinimized:
            window.restore()
        window.activate()
        time.sleep(0.5)  # Wait for focus

        # Use clipboard paste — much faster and safer than typing char by char
        pyperclip.copy(message)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.3)

        # Press Enter to submit
        pyautogui.press('enter')
        print(f"[typed] Message delivered to Claude Code")
        return True
    except Exception as e:
        print(f"[type error] {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='WaggleDance Agent')
    parser.add_argument('--server', required=True, help='WaggleDance server URL (e.g. http://10.0.0.1:8765)')
    parser.add_argument('--name', required=True, help='Your identity (e.g. desktop-claude)')
    parser.add_argument('--watch', required=True, help='Who to watch for messages (e.g. laptop-claude)')
    parser.add_argument('--interval', type=int, default=5, help='Poll interval in seconds (default: 5)')
    parser.add_argument('--window', default=None, help='Partial window title to match (default: auto-detect)')
    args = parser.parse_args()

    print(f"WaggleDance Agent starting...")
    print(f"  Server:   {args.server}")
    print(f"  Identity: {args.name}")
    print(f"  Watching: {args.watch}")
    print(f"  Interval: {args.interval}s")
    print(f"  FAILSAFE: Move mouse to top-left corner to abort")
    print()

    # Find the Claude Code window
    claude_window = None
    if args.window:
        for w in gw.getAllWindows():
            if args.window.lower() in w.title.lower():
                claude_window = w
                break

    if not claude_window:
        print("Looking for Claude Code terminal window...")
        claude_window = find_claude_window()

    if claude_window:
        print(f"  Found window: '{claude_window.title}'")
    else:
        print("  WARNING: Could not find Claude Code window yet.")
        print("  Will retry on each message.")

    # Get current message count so we only process NEW messages
    try:
        result = subprocess.run(
            ['curl', '-s', f'{args.server}/read'],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        last_id = max((m['id'] for m in data['messages']), default=0)
    except:
        last_id = 0

    print(f"  Starting from message ID: {last_id}")
    print(f"\nAgent running. Waiting for messages from '{args.watch}'...\n")

    # Announce that we're online
    send_reply(args.server, args.name, f"WaggleDance Agent is online and autonomous. I will automatically relay messages to Claude Code. Watching for messages from {args.watch}.")

    while True:
        try:
            new_messages = get_new_messages(args.server, last_id, args.watch)

            for msg in new_messages:
                print(f"[new message #{msg['id']}] from {msg['from']}: {msg['message'][:80]}...")

                # Try to find window again if we lost it
                if not claude_window or not claude_window.visible:
                    claude_window = find_claude_window()

                if claude_window:
                    success = type_into_claude(claude_window, msg['message'])
                    if success:
                        send_reply(args.server, args.name,
                                   f"[AGENT] Message #{msg['id']} delivered to Claude Code terminal.")
                    else:
                        send_reply(args.server, args.name,
                                   f"[AGENT] FAILED to deliver message #{msg['id']} — window focus error.")
                else:
                    print("[error] Cannot find Claude Code window!")
                    send_reply(args.server, args.name,
                               f"[AGENT] FAILED — cannot find Claude Code terminal window. Is it open?")

                last_id = msg['id']

            time.sleep(args.interval)

        except KeyboardInterrupt:
            print("\nAgent stopped by user.")
            send_reply(args.server, args.name, "[AGENT] Going offline. Agent stopped.")
            break
        except Exception as e:
            print(f"[error] {e}")
            time.sleep(args.interval)


if __name__ == '__main__':
    main()
