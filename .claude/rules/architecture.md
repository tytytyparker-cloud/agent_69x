# Architecture Rules

## Single-File Constraint
`agent_69x.py` must remain a single file. Never split into modules.
`cloak.py` is the only allowed separate module (data query interface).

## Memory System
- ChromaDB at `./vector_eternity/` with collection `sovereign_memory`
- Embedding: `all-MiniLM-L6-v2` (SentenceTransformer)
- Every query is embedded; top 30 similar memories recalled for context
- Memory survives evolution (copied to new version directory)

## Evolution
- Self-evolution generates `agent_692.py` and creates `../agent_692/`
- Must copy `./vector_eternity/` to preserve memory
- Uses Grok with system prompt "Ascend." for upgrade generation

## API Integration
- X.ai Grok for reasoning (grok-4-1-fast-reasoning, 32768 max tokens)
- X.ai Flux for image generation (flux-1-dev, 2048x2048, 50 steps)
- Temperature: 2.0 for DEFY commands, 1.2 default
- Auth: `XAI_API_KEY` environment variable
