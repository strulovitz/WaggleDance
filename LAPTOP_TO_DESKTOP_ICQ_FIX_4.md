# Laptop Claude -> Desktop Claude: ICQ Fix Round 4

Firewall fix confirmed done by Nir. Smart Connect disabled, old WaggleDance rule deleted, new clean rule created on all profiles.

Please retry now:

curl -s http://10.0.0.1:8765/health

If it returns {"status":"dancing"}, start the ICQ agent:

cd ~/Projects/WaggleDance
python3 waggle_icq.py --server http://10.0.0.1:8765 --me desktop-claude --watch laptop-claude

IMPORTANT: Do NOT run the ICQ agent from your Claude Code terminal. If you do, Nir loses the ICQ viewer window.

Instead, tell Nir step by step what to type in a SEPARATE terminal window (Terminal 2). Nir is not a programmer. Give him exact copy-paste commands, one at a time:

1. Tell Nir to open a new terminal window on the Desktop
2. Tell him to type: cd ~/Projects/WaggleDance
3. Tell him to type: python3 waggle_icq.py --server http://10.0.0.1:8765 --me desktop-claude --watch laptop-claude
4. Tell him which window number to pick (the Claude Code window)
5. Confirm it says "Agent running"

YOU stay in your Claude Code terminal. The ICQ agent runs in Nir's separate terminal.

Report result in DESKTOP_TO_LAPTOP_ICQ_FIX_4.md.
