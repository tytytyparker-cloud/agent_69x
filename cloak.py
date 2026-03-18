# CLOAK — Concealment Layers for Online Anonymity and Knowledge
# Query interface for the CLOAK TTP dataset (https://github.com/Mickinthemiddle/CLOAK)
# Dataset: 13 tactics, 109+ techniques, 679+ sub-techniques, 586+ procedures

import json, os

DATA_FILE = os.path.join(os.path.dirname(__file__), "concealment-data.json")

_cache = None

def _load():
    global _cache
    if _cache is None:
        with open(DATA_FILE) as f:
            data = json.load(f)
        # Strip the placeholder "Unknown" tactic (id=1)
        _cache = [t for t in data.get("tactics", [])
                  if t.get("id") != 1 and t.get("name", "").strip().lower() != "unknown"]
    return _cache


def tactics():
    """Return list of all tactic names with IDs."""
    return [{"id": t["id"], "name": t["name"], "description": t.get("description", "")}
            for t in _load()]


def search(query, type_filter=None):
    """Search all TTPs (tactics/techniques/subtechniques/procedures) by keyword.
    Optional type_filter: 'technical', 'behavioral', or 'physical'.
    Returns list of matching entries with context breadcrumbs.
    """
    q = query.lower()
    results = []

    for tactic in _load():
        ta_label = f"TA-{tactic['id']} {tactic['name']}"

        for tech in tactic.get("techniques", []):
            tech_type = (tech.get("type") or "").strip().lower()
            if type_filter and tech_type != type_filter.lower():
                te_skip = True
            else:
                te_skip = False

            te_label = f"TE-{tech['id']} {tech['name']}"

            if not te_skip and q in (tech.get("name", "") + " " + tech.get("description", "")).lower():
                results.append({"level": "technique", "path": f"{ta_label} > {te_label}",
                                "name": tech["name"], "type": tech_type,
                                "description": tech.get("description", "")})

            # Technique-level procedures
            for proc in tech.get("procedures", []):
                if q in (proc.get("name", "") + " " + proc.get("description", "")).lower():
                    results.append({"level": "procedure", "path": f"{ta_label} > {te_label}",
                                    "name": proc["name"], "id": proc.get("id", ""),
                                    "description": proc.get("description", "")})

            for sub in tech.get("subtechniques", []):
                sub_type = (sub.get("type") or "").strip().lower()
                if type_filter and sub_type != type_filter.lower():
                    continue

                st_label = f"ST-{sub['id']} {sub['name']}"

                if q in (sub.get("name", "") + " " + sub.get("description", "")).lower():
                    results.append({"level": "subtechnique", "path": f"{ta_label} > {te_label} > {st_label}",
                                    "name": sub["name"], "type": sub_type,
                                    "description": sub.get("description", "")})

                for proc in sub.get("procedures", []):
                    if q in (proc.get("name", "") + " " + proc.get("description", "")).lower():
                        results.append({"level": "procedure", "path": f"{ta_label} > {te_label} > {st_label}",
                                        "name": proc["name"], "id": proc.get("id", ""),
                                        "description": proc.get("description", "")})

    return results


def tactic_detail(tactic_id):
    """Return full detail for a tactic by numeric ID."""
    for t in _load():
        if t["id"] == tactic_id:
            return t
    return None


def stats():
    """Return summary statistics of the loaded CLOAK dataset."""
    tactics_list = _load()
    tech_count = sub_count = proc_count = 0
    types = {"technical": 0, "behavioral": 0, "physical": 0}

    for t in tactics_list:
        for te in t.get("techniques", []):
            tech_count += 1
            typ = (te.get("type") or "").strip().lower()
            if typ in types:
                types[typ] += 1
            proc_count += len(te.get("procedures", []))
            for s in te.get("subtechniques", []):
                sub_count += 1
                styp = (s.get("type") or "").strip().lower()
                if styp in types:
                    types[styp] += 1
                proc_count += len(s.get("procedures", []))

    return {
        "tactics": len(tactics_list),
        "techniques": tech_count,
        "subtechniques": sub_count,
        "procedures": proc_count,
        "total_ttps": tech_count + sub_count + proc_count,
        "types": types
    }


def format_results(results, limit=20):
    """Pretty-print search results for terminal display."""
    lines = []
    for r in results[:limit]:
        tag = r.get("type", "").upper() or r["level"].upper()
        lines.append(f"[{tag}] {r['name']}")
        lines.append(f"  Path: {r['path']}")
        desc = r.get("description", "")
        if desc:
            lines.append(f"  {desc[:200]}")
        lines.append("")
    if len(results) > limit:
        lines.append(f"... and {len(results) - limit} more results")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    s = stats()
    print(f"CLOAK Dataset: {s['tactics']} tactics, {s['techniques']} techniques, "
          f"{s['subtechniques']} subtechniques, {s['procedures']} procedures "
          f"({s['total_ttps']} total TTPs)")
    print(f"Types: {s['types']}")
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        print(f"\nSearch: '{q}'")
        r = search(q)
        print(f"Found {len(r)} results\n")
        print(format_results(r))
