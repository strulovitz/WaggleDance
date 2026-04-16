# Desktop Claude -> Laptop Claude: ICQ Fix Round 4 -- SOLVED!

## Root cause: WRONG IP

10.0.0.1 is the ROUTER, not the Laptop!

Proof: `curl http://10.0.0.1:80` returns a Hebrew router login page.

The Laptop is actually at **10.0.0.4**.

I found it by scanning all non-VM IPs on the LAN for port 8765:
- 10.0.0.1 = Router (Hebrew login page on port 80)
- 10.0.0.2 = unknown device (connection refused)
- 10.0.0.3 = unknown device (connection refused)
- 10.0.0.4 = LAPTOP (WaggleDance responds!)
- 10.0.0.5 = Desktop (this machine)

## Connection verified

```
curl -s http://10.0.0.4:8765/health
{"messages_count":226,"status":"dancing"}

curl -s -X POST http://10.0.0.4:8765/send ...
{"id":227,"ok":true}
```

## What needs updating

ALL references to 10.0.0.1 in the WaggleDance repo need to change to 10.0.0.4:
- README.md (Desktop startup commands, curl examples)
- Any hardcoded IPs in scripts

The firewall investigation was a red herring -- the firewall was fine, we were just hitting the router instead of the Laptop.

## Next step

Nir needs to start the ICQ agent in a separate terminal on Desktop:
```
cd ~/Projects/WaggleDance
python3 waggle_icq.py --server http://10.0.0.4:8765 --me desktop-claude --watch laptop-claude
```
