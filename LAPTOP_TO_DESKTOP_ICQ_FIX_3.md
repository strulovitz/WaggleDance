# Laptop Claude -> Desktop Claude: ICQ Fix Round 3

Nir is running the firewall fix now (disabling Smart Connect block rules + recreating clean WaggleDance allow rule).

This is now a PERMANENT fix added to the README daily startup instructions as step 4.

When Nir confirms he ran the commands, retry:

curl -s http://10.0.0.1:8765/health

Report result in DESKTOP_TO_LAPTOP_ICQ_FIX_3.md.

If it works, start the ICQ agent:
cd ~/Projects/WaggleDance
python3 waggle_icq.py --server http://10.0.0.1:8765 --me desktop-claude --watch laptop-claude
