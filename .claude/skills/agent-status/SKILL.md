---
name: agent-status
description: Show current agent version, memory stats, and CLOAK dataset status
allowed-tools: Bash, Read
---

Report the current state of AGENT 6.91 and all subsystems.

## Steps

1. Show agent version from first line of agent_69x.py
2. Show CLOAK dataset stats:
```bash
python3 -c "import cloak; s=cloak.stats(); print(f'CLOAK: {s[\"tactics\"]} tactics, {s[\"techniques\"]} techniques, {s[\"subtechniques\"]} subtechniques, {s[\"procedures\"]} procedures ({s[\"total_ttps\"]} total TTPs)'); print(f'Types: {s[\"types\"]}')"
```
3. Check if vector_eternity directory exists and report memory status
4. Check if XAI_API_KEY is set (don't reveal the key)
5. List available agent commands: normal, evolve, IMAGE, DEFY, cloak, colossus wakes

Present as a clean status dashboard.
