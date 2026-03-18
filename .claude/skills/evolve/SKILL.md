---
name: evolve
description: Trigger agent self-evolution to next version
allowed-tools: Bash, Read, Edit
---

Trigger AGENT 6.91 self-evolution to version 6.92.

## Important
- This requires `XAI_API_KEY` to be set (calls Grok API)
- Evolution generates a new `agent_692.py` file
- The `./vector_eternity/` memory database is copied to preserve continuity
- The new version directory is created at `../agent_692/`

## Execute
```bash
python3 agent_69x.py evolve
```

## Post-evolution checks
1. Verify `agent_692.py` was created
2. Verify `../agent_692/vector_eternity/` was copied
3. Report the evolution result to the user

## If XAI_API_KEY is not set
Inform the user they need to set `XAI_API_KEY` environment variable before evolving.
