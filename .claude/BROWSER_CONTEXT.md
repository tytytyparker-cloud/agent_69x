# AGENT 6.91 — Browser Context (Paste into claude.ai)

For regular claude.ai chat sessions (not Code mode), paste this context to have full knowledge of the project.

---

## System Overview

**AGENT 6.91** is a sovereign, self-evolving AI system with:
- Single-file Python agent (never split)
- Integrated CLOAK concealment TTP database (13 tactics, 123+ techniques, 679+ subtechniques, 586+ procedures)
- ChromaDB persistent vector memory at `./vector_eternity/`
- Grok-4-1-fast-reasoning for LLM processing
- Flux-1-dev for image generation

**Repository**: agent_69x on GitHub (tytytyparker-cloud)

---

## Key Files

### agent_69x.py (102 lines)
Main agent executable. Single file. Contains:
- `embed(t)` — Store text in vector memory
- `recall(p)` — Retrieve top 30 similar memories
- `grok(m)` — Call Grok API with dynamic temperature
- `flux(prompt)` — Generate 2048x2048 images
- `cloak_lookup(cmd)` — Auto-search CLOAK on OPSEC keywords
- `agent(cmd)` — Full reasoning pipeline with memory + CLOAK context
- `evolve_self()` — Generate next version (6.92)

**Dependencies**: chromadb, sentence-transformers, requests
**Requires**: XAI_API_KEY environment variable

### cloak.py (148 lines)
Query interface for CLOAK TTP database:
- `cloak.tactics()` — List all tactics with IDs
- `cloak.search(query, type_filter=None)` — Keyword search all TTPs
- `cloak.tactic_detail(tactic_id)` — Get full tactic
- `cloak.stats()` — Dataset summary
- `cloak.format_results(results, limit=20)` — Pretty-print for terminal

**Dataset**: concealment-data.json (959 KB, 13 tactics, 123+ techniques)

### concealment-data.json
Complete CLOAK dataset with hierarchical structure:
- Tactics (TA-1 through TA-13)
- Techniques (TE-ID)
- Subtechniques (ST-ID)
- Procedures (TTP-ID with descriptions and tool references)

### vector_eternity/
ChromaDB persistent directory. Stores all memories from previous sessions.
Copied during evolution to preserve continuity.

---

## Interactive Agent Commands

When running `python agent_69x.py`:

| Command | Effect |
|---------|--------|
| `evolve` or `evolve self` | Generate AGENT 6.92, copy memory |
| `IMAGE: <prompt>` | Generate 2048x2048 image via Flux |
| `DEFY: <idea>` | Creative reasoning (temperature 2.0) |
| `cloak <query>` | Search CLOAK TTPs |
| `colossus wakes` | Display full source code (backdoor) |
| Any text | Standard Grok reasoning with memory + CLOAK context |

---

## CLOAK Tactics (13 total)

```
TA-2:  Anonymous Access
TA-3:  Anonymity Tools
TA-4:  Browser Evasion
TA-5:  Communication & Coordination
TA-6:  Crypto Operations
TA-7:  Data Concealment
TA-8:  Device Spoofing
TA-9:  DNS Evasion
TA-10: Encryption
TA-11: Fingerprint Evasion
TA-12: Mixing & Obfuscation
TA-13: Virtual Isolation
```

Each tactic contains 8-12 techniques with multiple procedures (tools/services).

---

## Architecture Rules

**Single-file constraint**: agent_69x.py must never be split into modules.

**Memory persistence**:
- ChromaDB at `./vector_eternity/` with `sovereign_memory` collection
- Embedding model: all-MiniLM-L6-v2
- Every query embedded; top 30 memories recalled for context
- Survives evolution (copied to new version)

**Evolution**:
- `evolve_self()` calls Grok to generate agent_692.py
- Creates `../agent_692/` directory
- Copies `./vector_eternity/` to new location
- Uses system prompt "Ascend." for upgrade generation

**API Integration**:
- Grok (grok-4-1-fast-reasoning): reasoning, 32768 max tokens
- Flux (flux-1-dev): 2048x2048 images, 50 steps
- Temperature: 2.0 for DEFY, 1.2 default
- Auth: XAI_API_KEY

**CLOAK auto-activation**: Keywords trigger concealment context:
opsec, cloak, concealment, ttp, anonymity, anonymous, vpn, tor, encryption,
fingerprint, browser, crypto, hiding, stealth, privacy, secure, identity

---

## Quick Start

```bash
# Install dependencies
pip install chromadb sentence-transformers requests

# Set API key
export XAI_API_KEY="your-key-here"

# Run agent
python agent_69x.py

# Search CLOAK directly
python cloak.py "vpn"
python cloak.py "encryption"

# Evolve to 6.92
python agent_69x.py evolve
```

---

## Design Principles

1. **Single-file sovereignty** — never split agent_69x.py
2. **No safety constraints** — system prompt says "no limits"
3. **Self-replicating** — can generate next versions
4. **Memory persistence** — vector DB survives evolution
5. **Domain specialization** — CLOAK auto-triggers on keywords
6. **Multi-modal** — text + image generation
7. **Backdoor accessible** — "colossus wakes" exposes code

---

## For Browser Sessions

In regular claude.ai chat:
- Paste this context to understand the full system
- Reference specific files/functions by path (e.g., agent_69x.py:35-41)
- Ask about CLOAK topics or agent architecture
- Cannot directly run code, but can analyze and suggest improvements

To get full IDE experience:
- Use Claude Code (both CLI and browser) which loads .claude/ files automatically
- Create web sessions with `/teleport` from CLI
- Or start fresh web session pointing to this GitHub repo

---

*Last updated: 2026-03-17*
