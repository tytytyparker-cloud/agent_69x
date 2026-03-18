# CLOAK Knowledge Base Reference

CLOAK = Concealment Layers for Online Anonymity and Knowledge
Source: https://github.com/Mickinthemiddle/CLOAK

## Dataset Structure
Hierarchical: Tactics → Techniques → Subtechniques → Procedures
Each entry has: id, name, description, type (technical/behavioral/physical)

## Quick Reference — All 13 Tactics

Use `python cloak.py` for stats or `python cloak.py <query>` to search.
Use `import cloak; cloak.search("query")` in Python.

## API (cloak.py)
- `cloak.tactics()` — List all tactics with IDs and descriptions
- `cloak.search(query, type_filter=None)` — Keyword search across all TTPs
- `cloak.tactic_detail(tactic_id)` — Full detail for one tactic
- `cloak.stats()` — Summary counts
- `cloak.format_results(results, limit=20)` — Pretty-print for terminal

## Search Tips
- Search is case-insensitive keyword matching
- Optional type_filter: "technical", "behavioral", "physical"
- Returns up to 30 results with full context paths (tactic > technique > subtechnique)
- Results include: level, path, name, type, description

## Integration with Agent
In `agent_69x.py`, `cloak_lookup(cmd)` auto-triggers when query contains keywords:
opsec, cloak, concealment, ttp, anonymity, anonymous, vpn, tor, encryption,
fingerprint, browser, crypto, hiding, stealth, privacy, secure, identity
