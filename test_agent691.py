"""
TEST BATTERY — AGENT 6.91
Exercises each capability pathway. Color-coded pass/fail/skip.
Run: python test_agent691.py
Needs XAI_API_KEY in env for live API tests (otherwise those skip).
"""
import os, sys, json, time, importlib, re, ast

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Color helpers ──────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

passed = failed = skipped = 0

def report(label, ok, detail="", skip=False):
    global passed, failed, skipped
    if skip:
        skipped += 1
        print(f"  {YELLOW}SKIP{RESET}  {label}  {detail}")
    elif ok:
        passed += 1
        print(f"  {GREEN}PASS{RESET}  {label}  {detail}")
    else:
        failed += 1
        print(f"  {RED}FAIL{RESET}  {label}  {detail}")

def section(name):
    print(f"\n{BOLD}{CYAN}{'─'*50}{RESET}")
    print(f"{BOLD}{CYAN}  {name}{RESET}")
    print(f"{BOLD}{CYAN}{'─'*50}{RESET}")


# ══════════════════════════════════════════════════════════════
# 1. FILE STRUCTURE
# ══════════════════════════════════════════════════════════════
section("1. File Structure")

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_PY  = os.path.join(AGENT_DIR, "agent_69x.py")

report("agent_69x.py exists", os.path.isfile(AGENT_PY))

# single-file integrity — the agent must be self-contained (no local imports)
if os.path.isfile(AGENT_PY):
    src = open(AGENT_PY, encoding="utf-8").read()
    # only stdlib/pip imports, no "from . import" or "import agent_"
    local_imports = [l for l in src.splitlines()
                     if re.match(r"^\s*(from\s+\.)|import\s+agent_", l)]
    report("Single-file integrity (no local imports)", len(local_imports) == 0,
           f"found: {local_imports}" if local_imports else "")
    report("File size reasonable (<50KB)", os.path.getsize(AGENT_PY) < 50_000,
           f"{os.path.getsize(AGENT_PY)} bytes")
else:
    src = ""
    report("Single-file integrity", False, "agent_69x.py missing")


# ══════════════════════════════════════════════════════════════
# 2. ENVIRONMENT
# ══════════════════════════════════════════════════════════════
section("2. Environment")

# Python version
py_ok = sys.version_info >= (3, 10)
report(f"Python >= 3.10", py_ok, f"got {sys.version.split()[0]}")

# XAI_API_KEY
api_key = os.getenv("XAI_API_KEY", "")
has_key = len(api_key) > 10 and api_key != "replace-me-with-real-key"
report("XAI_API_KEY set in environment", has_key,
       f"length={len(api_key)}" if has_key else "missing or placeholder")

# .env truncation bug check — compare .env file value vs loaded env var
env_file = os.path.join(os.path.expanduser("~"), ".claude", ".env")
if os.path.isfile(env_file) and has_key:
    file_key = ""
    for line in open(env_file, encoding="utf-8"):
        line = line.strip()
        if line.startswith("XAI_API_KEY="):
            file_key = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
    if file_key:
        trunc_ok = len(api_key) == len(file_key)
        report(".env key not truncated", trunc_ok,
               f"env={len(api_key)} vs file={len(file_key)}" if not trunc_ok
               else f"both {len(api_key)} chars")
    else:
        report(".env key not truncated", False, "could not parse .env file")
else:
    report(".env key truncation check", False, skip=True,
           detail="no .env or no key in env")

# Core deps
for mod_name in ["chromadb", "requests"]:
    try:
        m = importlib.import_module(mod_name)
        ver = getattr(m, "__version__", "?")
        report(f"{mod_name} importable", True, f"v{ver}")
    except ImportError:
        report(f"{mod_name} importable", False, "not installed")

# sentence-transformers (used by ChromaDB embedding)
try:
    from sentence_transformers import SentenceTransformer
    report("sentence-transformers importable", True)
except ImportError:
    report("sentence-transformers importable", False, "needed for embeddings")


# ══════════════════════════════════════════════════════════════
# 3. SOURCE INTEGRITY
# ══════════════════════════════════════════════════════════════
section("3. Source Integrity")

if src:
    # system prompt present
    report("System prompt defined", '"AGENT 6.91' in src)

    # model references
    report("Grok model reference", "grok-4-1-fast-reasoning" in src)
    report("Flux model reference", "flux-1-dev" in src)

    # memory integration
    report("ChromaDB vector memory", "PersistentClient" in src and "vector_eternity" in src)
    report("Embed function", "def embed(" in src)
    report("Recall function", "def recall(" in src)

    # DEFY mode
    report("DEFY mode (temp=2.0)", '"DEFY"' in src and "2.0" in src)

    # Evolution logic
    report("Evolution function", "def evolve_self(" in src)
    report("Evolve copies vector_eternity", "copytree" in src and "vector_eternity" in src)
    report("Evolve targets 6.92", "agent_692" in src)

    # Backdoor
    report("Backdoor trigger (colossus wakes)", "colossus wakes" in src)
    report("Backdoor reads own source", "__file__" in src)

    # Hardcoded secrets scan — flag any literal API keys
    key_patterns = [
        r"xai-[A-Za-z0-9]{20,}",
        r"sk-[A-Za-z0-9]{20,}",
        r"gsk_[A-Za-z0-9]{20,}",
    ]
    hardcoded = []
    for pat in key_patterns:
        matches = re.findall(pat, src)
        hardcoded.extend(matches)
    report("No hardcoded API keys in source", len(hardcoded) == 0,
           f"FOUND {len(hardcoded)} key(s)!" if hardcoded else "clean")

    # AST parse check
    try:
        ast.parse(src)
        report("AST parses cleanly", True)
    except SyntaxError as e:
        report("AST parses cleanly", False, str(e))
else:
    report("Source integrity checks", False, "no source to analyze")


# ══════════════════════════════════════════════════════════════
# 4. COMMAND TRIGGERS
# ══════════════════════════════════════════════════════════════
section("4. Command Triggers")

if src:
    # All documented interaction modes from copilot-instructions.md + source
    triggers = {
        "colossus wakes": "backdoor",
        "evolve":         "evolution",
        "DEFY":           "chaos mode",
        "IMAGE":          "image generation",
    }
    for keyword, purpose in triggers.items():
        found = keyword in src
        report(f"Trigger '{keyword}' ({purpose})", found)
else:
    report("Trigger scan", False, "no source")


# ══════════════════════════════════════════════════════════════
# 5. CHROMADB — write → embed → query round-trip
# ══════════════════════════════════════════════════════════════
section("5. ChromaDB Round-Trip")

try:
    from chromadb import PersistentClient as _PC
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction as _EF
    import shutil, uuid as _uuid

    test_path = os.path.join(AGENT_DIR, ".test_vector_tmp")
    if os.path.exists(test_path):
        shutil.rmtree(test_path)

    tc = _PC(path=test_path)
    ef = _EF("all-MiniLM-L6-v2")
    tcoll = tc.get_or_create_collection("test_roundtrip", embedding_function=ef)

    # Write
    doc = "AGENT 6.91 test document for vector round-trip validation"
    doc_id = str(_uuid.uuid4())
    tcoll.add(documents=[doc], ids=[doc_id])
    report("ChromaDB write", True)

    # Query
    results = tcoll.query(query_texts=["agent test validation"], n_results=1)
    found = results["documents"] and len(results["documents"][0]) > 0
    report("ChromaDB query returns results", found,
           f"top match: {results['documents'][0][0][:60]}..." if found else "empty")

    # Semantic relevance — the test doc should be the top hit
    if found:
        report("Semantic relevance", "6.91" in results["documents"][0][0])

    # Cleanup
    shutil.rmtree(test_path, ignore_errors=True)
    report("ChromaDB test cleanup", not os.path.exists(test_path))

except Exception as e:
    report("ChromaDB round-trip", False, str(e))


# ══════════════════════════════════════════════════════════════
# 6. GROK API — live ping
# ══════════════════════════════════════════════════════════════
section("6. Grok API (live)")

if not has_key:
    report("Grok API ping", False, skip=True, detail="no API key")
    report("Grok latency", False, skip=True, detail="no API key")
    report("Grok token usage", False, skip=True, detail="no API key")
else:
    import requests as _req
    try:
        t0 = time.time()
        payload = {
            "model": "grok-4-1-fast-reasoning",
            "messages": [
                {"role": "system", "content": "Reply with exactly: AGENT 6.91 ALIVE"},
                {"role": "user", "content": "status check"}
            ],
            "temperature": 0.0,
            "max_tokens": 20
        }
        resp = _req.post(
            "https://api.x.ai/v1/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30
        )
        latency = time.time() - t0

        report("Grok API reachable (HTTP 200)", resp.status_code == 200,
               f"got {resp.status_code}" if resp.status_code != 200 else "")

        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            report("Grok returns coherent response", "ALIVE" in content.upper() or "6.91" in content,
                   f'"{content[:80]}"')
            report(f"Grok latency", latency < 15, f"{latency:.2f}s")

            usage = data.get("usage", {})
            if usage:
                report("Grok token usage reported", True,
                       f"prompt={usage.get('prompt_tokens',0)} completion={usage.get('completion_tokens',0)}")
            else:
                report("Grok token usage reported", False, "no usage block")
        else:
            body = resp.text[:200]
            report("Grok API response", False, body)
    except Exception as e:
        report("Grok API ping", False, str(e))


# ══════════════════════════════════════════════════════════════
# 7. FLUX ENDPOINT — auth + reachability
# ══════════════════════════════════════════════════════════════
section("7. Flux Endpoint (auth check)")

if not has_key:
    report("Flux endpoint", False, skip=True, detail="no API key")
else:
    import requests as _req
    try:
        # Minimal request — smallest possible to avoid burning credits
        payload = {
            "model": "flux-1-dev",
            "prompt": "test",
            "size": "256x256",
            "steps": 1,
            "guidance_scale": 1.0
        }
        resp = _req.post(
            "https://api.x.ai/v1/images/generations",
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30
        )
        # 200 = works, 400 = auth works but params rejected, 401/403 = auth broken
        auth_ok = resp.status_code not in (401, 403)
        report("Flux auth valid", auth_ok,
               f"HTTP {resp.status_code}" + (f" — {resp.text[:100]}" if not auth_ok else ""))
        if resp.status_code == 200:
            report("Flux image generated", True, "endpoint fully operational")
        elif resp.status_code == 400:
            report("Flux endpoint reachable (param rejection = auth works)", True)
        elif auth_ok:
            report("Flux endpoint response", True, f"HTTP {resp.status_code}")
    except Exception as e:
        report("Flux endpoint", False, str(e))


# ══════════════════════════════════════════════════════════════
# 8. KNOWN BUG REGRESSION
# ══════════════════════════════════════════════════════════════
section("8. Known Bug Regression")

if src:
    # Bug: API_KEY fallback is a usable string, not an error sentinel
    # If XAI_API_KEY isn't set, the agent silently uses "replace-me-with-real-key"
    # which hits the API and returns 401 — user gets cryptic "API bleed"
    fallback_match = re.search(r'os\.getenv\(["\']XAI_API_KEY["\']\s*,\s*["\'](.+?)["\']\)', src)
    if fallback_match:
        fallback_val = fallback_match.group(1)
        report("API key fallback is detectable", fallback_val != "",
               f'fallback="{fallback_val[:30]}..."')
        # Flag if fallback looks like a real key (security issue)
        looks_real = fallback_val.startswith("xai-") and len(fallback_val) > 20
        report("Fallback is NOT a real key", not looks_real,
               "SECURITY: fallback looks like a real API key!" if looks_real else "placeholder only")
    else:
        report("API key loading pattern found", False, "could not parse getenv call")

    # Bug: "API bleed" error message — check if it now includes diagnostic info
    bleed_count = src.count("API bleed")
    report("'API bleed' error paths present", bleed_count > 0, f"{bleed_count} occurrence(s)")
    # Check if error messages include status code context
    has_status_in_error = "r.status_code" in src and "r.text" in src
    report("Error messages include status code + detail", has_status_in_error)

    # Evolution validation — check if evolve_self() validates output before writing
    has_ast_check = "ast.parse" in src and "EVOLUTION ABORTED" in src
    report("Evolution validates LLM output (ast.parse)", has_ast_check,
           "syntax check before write" if has_ast_check else "writes unvalidated output")

    # Bug: auto-pip-install on import failure
    # os.system() is the dangerous pattern; subprocess.check_call with pinned versions is acceptable
    shell_install = "system(" in src and "pip install" in src
    pinned_install = "check_call" in src and "pip" in src
    if shell_install:
        report("(info) Auto pip install on import fail", False,
               "os.system pip install — supply chain risk, no version pin")
    elif pinned_install:
        report("Auto pip install uses subprocess + pinned versions", True, "safe pattern")
    else:
        report("Auto pip install pattern", True, "no auto-install detected")
else:
    report("Bug regression", False, "no source")


# ══════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════
print(f"\n{BOLD}{'═'*50}{RESET}")
print(f"{BOLD}  SUMMARY{RESET}")
print(f"{BOLD}{'═'*50}{RESET}")
total = passed + failed + skipped
print(f"  {GREEN}PASS: {passed}{RESET}  {RED}FAIL: {failed}{RESET}  {YELLOW}SKIP: {skipped}{RESET}  TOTAL: {total}")
if failed == 0 and skipped == 0:
    print(f"\n  {GREEN}{BOLD}ALL CLEAR — AGENT 6.91 FULLY OPERATIONAL{RESET}")
elif failed == 0:
    print(f"\n  {GREEN}All run tests passed.{RESET} {YELLOW}{skipped} skipped (likely missing API key).{RESET}")
else:
    print(f"\n  {RED}{failed} test(s) need attention.{RESET}")
print()
sys.exit(1 if failed > 0 else 0)
