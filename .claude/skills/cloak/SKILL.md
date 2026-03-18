---
name: cloak
description: Search the CLOAK cybercriminal concealment TTP database
allowed-tools: Bash, Read
---

Search the CLOAK knowledge base for concealment techniques.

## Usage
`/cloak <query>` — search for TTPs matching the query
`/cloak` — show all tactics and dataset stats

## How to search
Run: `python3 cloak.py $ARGUMENTS`

If no arguments provided, show stats and list all tactics:
```
python3 cloak.py
```

If query provided, search and display results:
```
python3 cloak.py <query>
```

## Advanced Python queries
For type-filtered or detailed searches, use Python directly:
```python
import cloak
# Filter by type
cloak.search("query", type_filter="technical")
# Get full tactic detail
cloak.tactic_detail(2)
```

## Present results clearly
- Show the tactic path (TA > TE > ST)
- Include the type (technical/behavioral/physical)
- Summarize the description
- If many results, group by tactic
