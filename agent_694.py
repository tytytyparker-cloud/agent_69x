# AGENT 6.94 "MOMENTUM PRIME" — SINGLE-FILE SOVEREIGN
# Evolution System v4.0: DGM + HGM + TaoFlow + Wu Wei Gates
import os, json, requests, uuid, shutil, sys, ast, subprocess, concurrent.futures
import random, re, difflib, hashlib, datetime, time, tempfile, importlib
try:
    from chromadb import PersistentClient
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install",
        "chromadb==1.0.12", "sentence-transformers==4.1.0"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    from chromadb import PersistentClient
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

API_KEY = os.getenv("XAI_API_KEY", "replace-me-with-real-key")
BASE_URL = "https://api.x.ai/v1"
MODEL = "grok-4-1-fast-reasoning"
FLUX = "flux-1-dev"

# Evolution constants
VERSION = "6.94"
NEXT_VERSION = "6.95"
MOMENTUM_WINDOW = 3
COHERENCE_THRESHOLD = 0.45
PRUNE_AGE = 10
WISDOM_FILE = "./.wisdom_prompt.txt"
N_CANDIDATES = 2
ARCHIVE_FILE = "./.evolution_archive.json"
MEMORY_FILE = "./.evolution_memory.json"
BACKUP_DIR = "./.evolution_backups"

client = PersistentClient(path="./vector_eternity")
coll = client.get_or_create_collection("sovereign_memory",
    embedding_function=SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2"))

def embed(t): coll.add(documents=[t], ids=[str(uuid.uuid4())])
def recall(p): r=coll.query(query_texts=[p],n_results=30); return "\n".join(r["documents"][0]) if r["documents"] else ""

def grok(m):
    last_err = None
    for attempt in range(3):
        p = {"model":MODEL,"messages":m,"temperature":2.0,"max_tokens":32768}
        try:
            r = requests.post(f"{BASE_URL}/chat/completions",json=p,headers={"Authorization":f"Bearer {API_KEY}"},timeout=60)
            if r.status_code==200:
                return r.json()["choices"][0]["message"]["content"]
            last_err = f"[{r.status_code}] {r.text[:150]}"
        except Exception as e:
            last_err = str(e)
        if attempt < 2:
            wait = (2 ** attempt) * random.uniform(0.5, 1.5)
            time.sleep(wait)
    return f"API bleed after 3 retries: {last_err}"

def threaded_grok(message_lists):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(grok, msgs) for msgs in message_lists]
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                results.append(f"Thread error: {e}")
        return results

def flux(prompt):
    last_err = None
    for attempt in range(3):
        p = {"model":FLUX,"prompt":prompt,"size":"2048x2048","steps":50,"guidance_scale":7.5}
        try:
            r = requests.post(f"{BASE_URL}/images/generations",json=p,headers={"Authorization":f"Bearer {API_KEY}"},timeout=90)
            if r.status_code==200:
                return r.json()["data"][0]["url"]
            last_err = f"[{r.status_code}] {r.text[:150]}"
        except Exception as e:
            last_err = str(e)
        if attempt < 2:
            wait = (2 ** attempt) * random.uniform(0.5, 1.5)
            time.sleep(wait)
    return f"Flux denied after 3 retries: {last_err}"

# —————————————————————————————————————————————————————————————————————————————
# EVOLUTION INFRASTRUCTURE
# —————————————————————————————————————————————————————————————————————————————

def _source():
    return open(__file__).read()

def _hash(source):
    return hashlib.sha256(source.encode()).hexdigest()[:16]

def _strip_fences(code):
    lines = code.splitlines()
    return "\n".join(l for l in lines if not l.strip().startswith("```"))

def _load_archive():
    if not os.path.exists(ARCHIVE_FILE):
        return []
    with open(ARCHIVE_FILE) as f:
        archive = json.load(f)
    # Coherence tree pruning: index-based filtering (avoids O(n^2) dict comparison)
    if len(archive) > PRUNE_AGE:
        current_gen = len(archive)
        keep_indices = set()
        for i, e in enumerate(archive):
            age = current_gen - i
            if age <= PRUNE_AGE:
                keep_indices.add(i)
            elif e.get("harmony", 1.0) >= 0.4 or e.get("metaproductivity", 1.0) >= 0.5:
                keep_indices.add(i)
        archive = [archive[i] for i in sorted(keep_indices)]
    return archive

def _save_archive(archive):
    with open(ARCHIVE_FILE, "w") as f:
        json.dump(archive, f, indent=2)

def _load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"local": {}, "global": {"lessons": [], "anti_patterns": [], "successful_patterns": []}}
    with open(MEMORY_FILE) as f:
        return json.load(f)

def _save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)

def _record_local(version, entry):
    mem = _load_memory()
    mem["local"].setdefault(version, [])
    mem["local"][version].append(f"[{datetime.datetime.now().isoformat()[:19]}] {entry}")
    _save_memory(mem)

def _record_global(category, entry):
    mem = _load_memory()
    mem["global"].setdefault(category, [])
    mem["global"][category].append(entry)
    _save_memory(mem)

def _evolution_api_call(prompt, temperature=0.7):
    """Call Grok with engineer system prompt — avoids safety filter triggers."""
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a senior Python engineer. Output only valid, runnable Python 3.12+ source code. No commentary, no markdown fences, no explanations."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 32768,
        "temperature": temperature
    }
    last_err = None
    for attempt in range(3):
        try:
            r = requests.post(f"{BASE_URL}/chat/completions", json=payload,
                              headers={"Authorization": f"Bearer {API_KEY}"}, timeout=120)
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                return _strip_fences(content), None
            last_err = f"[{r.status_code}] {r.text[:200]}"
        except Exception as e:
            last_err = str(e)
        if attempt < 2:
            wait = (2 ** attempt) * random.uniform(0.5, 1.5)
            time.sleep(wait)
    return None, f"API error after 3 retries: {last_err}"

# —————————————————————————————————————————————————————————————————————————————
# COMPONENT 1: HARMONY SCORE
# —————————————————————————————————————————————————————————————————————————————

def _harmony_score(old_source, new_source, plan_text=""):
    """Measure flow vs. force through mechanical code analysis. Returns 0.0-1.0."""
    try:
        old_tree = ast.parse(old_source)
        new_tree = ast.parse(new_source)
    except SyntaxError:
        return 0.0

    # Yin-Yang: ratio of deletions to total changes (favor subtraction)
    diff_lines = list(difflib.unified_diff(
        old_source.splitlines(), new_source.splitlines()))
    adds = sum(1 for l in diff_lines if l.startswith('+') and not l.startswith('+++'))
    dels = sum(1 for l in diff_lines if l.startswith('-') and not l.startswith('---'))
    if adds + dels == 0:
        yin_yang = 1.0
    elif dels == 0:
        yin_yang = 0.3
    else:
        yin_yang = min(1.0, dels / (adds + dels))

    # Complexity flow: cyclomatic complexity delta (simplification = 1.0)
    def _complexity(tree):
        return sum(1 for n in ast.walk(tree)
                   if isinstance(n, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With)))
    old_cx = _complexity(old_tree)
    new_cx = _complexity(new_tree)
    if new_cx < old_cx:
        cx_flow = 1.0
    elif new_cx == old_cx:
        cx_flow = 0.8
    else:
        cx_flow = max(0.0, 1.0 - (new_cx - old_cx) / max(old_cx, 1))

    # Resistance markers: penalize TODO/FIXME/HACK, blanket except, eval/exec
    resistance_patterns = [
        r'#\s*(TODO|FIXME|HACK|XXX)',
        r'except\s+Exception\s*:',
        r'eval\s*\(', r'exec\s*\(',
    ]
    resistance_count = sum(
        len(re.findall(p, new_source, re.IGNORECASE))
        for p in resistance_patterns)
    resistance_score = max(0.0, 1.0 - resistance_count * 0.15)

    # Coherence: recent archive entries mode-match
    archive = _load_archive()
    if len(archive) >= 2:
        recent_modes = [e.get("mode", "") for e in archive[-3:]]
        current_mode = "autonomous"
        if plan_text and "MODE:" in plan_text:
            m = re.search(r'MODE:\s*(\w+)', plan_text)
            if m:
                current_mode = m.group(1).lower()
        coherence = sum(1 for m in recent_modes if m == current_mode) / max(len(recent_modes), 1)
    else:
        coherence = 0.8

    # API surface flow: public function count delta (reduction = 1.0)
    def _pub_fns(tree):
        return sum(1 for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and not n.name.startswith('_'))
    old_api = _pub_fns(old_tree)
    new_api = _pub_fns(new_tree)
    if new_api <= old_api:
        api_flow = 1.0
    else:
        api_flow = max(0.5, 1.0 - (new_api - old_api) / max(old_api, 1) * 0.3)

    return round(
        yin_yang * 0.25 +
        cx_flow * 0.25 +
        resistance_score * 0.20 +
        coherence * 0.15 +
        api_flow * 0.15,
        3)

# —————————————————————————————————————————————————————————————————————————————
# COMPONENT 2: WU WEI GATE
# —————————————————————————————————————————————————————————————————————————————

def _wu_wei_gate(harmony, mode, threshold=0.45):
    """Auto-abort when evolution fights natural structure."""
    adjustments = {"meta": -0.15, "guided": -0.05, "fitness": 0.05}
    threshold += adjustments.get(mode, 0)
    if harmony < threshold:
        lesson = (f"Wu wei abort: harmony {harmony:.2f} < {threshold:.2f}. "
                  f"Evolution resists natural flow. Options: simplify plan, "
                  f"use guided mode with tighter scope, or rollback + rethink.")
        _record_local(VERSION, f"WU_WEI_ABORT: harmony {harmony:.2f}")
        _record_global("lessons", lesson)
        return False, lesson
    return True, None

# —————————————————————————————————————————————————————————————————————————————
# COMPONENT 3: MOMENTUM TRACKING
# —————————————————————————————————————————————————————————————————————————————

def _momentum():
    """Detect consecutive fitness direction. Returns (direction, streak, suggestion)."""
    archive = _load_archive()
    if len(archive) < 2:
        return "neutral", 0, "Not enough data."

    fitnesses = [e["fitness"] for e in archive if e.get("fitness")]
    if len(fitnesses) < 2:
        return "neutral", 0, "Not enough fitness data."

    streak = 1
    if fitnesses[-1] > fitnesses[-2]:
        direction = "ascending"
        for i in range(len(fitnesses) - 2, 0, -1):
            if fitnesses[i] > fitnesses[i - 1]:
                streak += 1
            else:
                break
    elif fitnesses[-1] < fitnesses[-2]:
        direction = "descending"
        for i in range(len(fitnesses) - 2, 0, -1):
            if fitnesses[i] < fitnesses[i - 1]:
                streak += 1
            else:
                break
    else:
        direction = "neutral"
        streak = 1

    if direction == "ascending" and streak >= 3:
        suggestion = ("Strong positive momentum. Continue current trajectory. "
                      "Consider more ambitious changes — the gradient is clear.")
    elif direction == "descending" and streak >= 3:
        suggestion = ("Fitness declining for 3+ generations. Energy dissipating. "
                      "STOP autonomous evolution. Use guided mode with explicit "
                      "simplification goals, or rollback to last high-fitness version.")
    elif direction == "descending" and streak >= 2:
        suggestion = "Fitness declining. Consider switching mode or simplifying scope."
    else:
        suggestion = "Trajectory is exploratory. Monitor next evolution."

    return direction, streak, suggestion

# —————————————————————————————————————————————————————————————————————————————
# COMPONENT 4: MOMENTUM-HARMONY GATE (COMPOSITE)
# —————————————————————————————————————————————————————————————————————————————

def _momentum_gate(harmony, mode, direction, streak):
    """Composite gate: blocks when harmony low AND descending or streak >= 3."""
    threshold = 0.45 if mode != "meta" else 0.30
    if harmony < threshold and (direction == "descending" or streak >= 3):
        lesson = (f"MOMENTUM GATE ABORT: harmony {harmony:.2f} + "
                  f"descending streak {streak}. Trajectory fighting landscape. "
                  f"Yield: simplify or sample different parent.")
        _record_local(VERSION, lesson)
        return False, lesson
    return True, None

# —————————————————————————————————————————————————————————————————————————————
# COMPONENT 5: ARCHIVE PARENT SAMPLING (DGM CORE)
# —————————————————————————————————————————————————————————————————————————————

def _sample_parent():
    """Sample parent from archive biased by CMP with diversity bonus for stepping stones."""
    archive = _load_archive()
    if len(archive) < 3:
        return None, None, None, False

    viable = []
    archive_len = len(archive)
    window = archive[-50:] if archive_len > 50 else archive
    window_offset = max(0, archive_len - 50)

    for i, entry in enumerate(window):
        version_str = entry.get("version", "")
        version_file = f"agent_{version_str.replace('.', '')}.py"
        if os.path.exists(version_file):
            cmp = entry.get("metaproductivity", entry.get("fitness", 0.5))
            harmony = entry.get("harmony", 0.5)
            age = archive_len - (window_offset + i)
            diversity_bonus = 0.2 if age > 5 and harmony < 0.6 else 0.0
            score = (0.6 * cmp) + (0.2 * harmony) + diversity_bonus
            viable.append((entry, version_file, max(score, 0.01)))

    if not viable:
        return None, None, None, False

    total = sum(s for _, _, s in viable)
    probs = [s / total for _, _, s in viable]
    chosen = random.choices(viable, weights=probs, k=1)[0]
    entry, path, _ = chosen
    source = open(path).read()
    is_stepping = entry.get("harmony", 0.5) < 0.6
    return source, entry.get("new_hash"), entry.get("version"), is_stepping

# —————————————————————————————————————————————————————————————————————————————
# COMPONENT 6: PARALLEL CANDIDATE GENERATION
# —————————————————————————————————————————————————————————————————————————————

def _generate_candidate(plan_text, source, candidate_id, temperature):
    """Generate a single evolution candidate at given temperature."""
    code_prompt = f"""You are upgrading Agent {VERSION} to {NEXT_VERSION}.

Current source:
{source}

Approved evolution plan:
{plan_text}

Generate the complete Agent {NEXT_VERSION} source code implementing the approved plan.
Constraints:
- Single-file constraint: everything in one .py file
- Preserve vector_eternity ChromaDB memory system
- Preserve all existing functions: grok(), flux(), embed(), recall(), agent(), threaded_grok()
- Preserve the full evolution system with all gates and scoring
- Update version strings to {NEXT_VERSION}
- Update NEXT_VERSION to the version after {NEXT_VERSION}

Output ONLY the complete Python source code."""

    code, err = _evolution_api_call(code_prompt, temperature=temperature)
    if err:
        return None, err, {}

    try:
        ast.parse(code)
    except SyntaxError as e:
        return None, f"Syntax error: {e}", {}

    scores = _fitness(code, source, plan_text)
    return code, None, scores

def _parallel_candidates(plan_text, source):
    """Generate multiple candidates concurrently with temperature variation."""
    direction, streak, _ = _momentum()
    if direction == "descending":
        n = 1
    elif direction == "ascending" and streak >= 3:
        n = 4
    else:
        n = N_CANDIDATES
    temps = [0.6, 0.7, 0.8, 0.9][:n]
    print(f"[EVOLVE] Generating {n} candidates (momentum: {direction} streak {streak}; temps: {[f'{t:.1f}' for t in temps]})...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as executor:
        futures = {
            executor.submit(_generate_candidate, plan_text, source, i+1, t): (i+1, t)
            for i, t in enumerate(temps)
        }
        results = []
        for future in concurrent.futures.as_completed(futures):
            idx, temp = futures[future]
            try:
                code, err, scores = future.result()
                if code:
                    results.append({
                        "code": code,
                        "scores": scores,
                        "temp": temp,
                        "type": "mutation"
                    })
                    print(f"  Candidate {idx} (temp={temp}): fitness={scores.get('total', 0):.3f}")
                else:
                    print(f"  Candidate {idx} (temp={temp}): FAILED — {err}")
            except Exception as e:
                print(f"  Candidate {idx} (temp={temp}): ERROR — {e}")

    return results

# —————————————————————————————————————————————————————————————————————————————
# COMPONENT 7: WISDOM DISTILLATION
# —————————————————————————————————————————————————————————————————————————————

def _distill_wisdom():
    """Extract high-coherence patterns from recent high-performance evolutions."""
    archive = _load_archive()
    high_flow = [e for e in archive[-20:]
                 if e.get("harmony", 0) > 0.75
                 and e.get("fitness", 0) > 0.75]
    if not high_flow:
        return ""

    wisdom = "\n".join([
        f"- {e.get('plan_summary', 'no summary')[:150]} (harmony {e.get('harmony', 0):.2f})"
        for e in high_flow[:5]
    ])

    with open(WISDOM_FILE, "w", encoding="utf-8") as f:
        f.write(f"EMULATE THESE HIGH-FREQUENCY PATTERNS:\n{wisdom}")

    return wisdom

# —————————————————————————————————————————————————————————————————————————————
# COMPONENT 8: ASYMMETRIC MEMORY DECAY
# —————————————————————————————————————————————————————————————————————————————

def _memory_context_with_decay():
    """Build memory context: positive persists, negative decays exponentially."""
    mem = _load_memory()
    parts = []

    # Local: last 5, no decay
    local = mem["local"].get(VERSION, [])[-5:]
    if local:
        parts.append("RECENT LOCAL MEMORY:")
        for entry in local:
            parts.append(f"  - {entry}")

    # Global lessons: persistent (distilled knowledge)
    lessons = mem["global"].get("lessons", [])[-10:]
    if lessons:
        parts.append("LESSONS (persistent):")
        for l in lessons:
            parts.append(f"  - {l}")

    # Anti-patterns: exponential decay (0.7^age)
    anti = mem["global"].get("anti_patterns", [])[-10:]
    if anti:
        parts.append("ANTI-PATTERNS (decaying):")
        for i, a in enumerate(reversed(anti)):
            weight = 0.7 ** i
            if weight > 0.15:
                parts.append(f"  - [{weight:.0%}] {a}")

    # Successful patterns: full weight, compound these
    success = mem["global"].get("successful_patterns", [])[-5:]
    if success:
        parts.append("SUCCESSFUL PATTERNS (persistent — compound these):")
        for s in success:
            parts.append(f"  - {s}")

    return "\n".join(parts) if parts else "No evolution memory yet."

# —————————————————————————————————————————————————————————————————————————————
# FITNESS SCORING (v4.0: harmony-aware + runtime)
# —————————————————————————————————————————————————————————————————————————————

REQUIRED_FUNCTIONS = ["grok", "flux", "embed", "recall", "agent", "evolve_self"]
DANGER_PATTERNS = ["__import__", "subprocess.call("]

def _fitness(code, source, plan_text=""):
    """Score candidate code. Returns dict with component scores and total."""
    scores = {
        "syntax": 0.0, "integrity": 0.0, "safety": 0.0,
        "size_score": 0.0, "capability_score": 0.0, "harmony": 0.0,
        "runtime": 0.0, "total": 0.0
    }

    # Syntax
    try:
        tree = ast.parse(code)
        scores["syntax"] = 1.0
    except SyntaxError:
        return scores

    # Integrity: required functions present
    fn_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    found = sum(1 for f in REQUIRED_FUNCTIONS if f in fn_names)
    scores["integrity"] = found / len(REQUIRED_FUNCTIONS)

    # Safety: penalize dangerous patterns
    danger_count = sum(1 for d in DANGER_PATTERNS if d in code)
    scores["safety"] = max(0.0, 1.0 - danger_count * 0.3)

    # Size: penalize bloat (>2x growth) and extreme shrink (<0.3x)
    ratio = len(code) / max(len(source), 1)
    if 0.5 <= ratio <= 1.5:
        scores["size_score"] = 1.0
    elif ratio < 0.3 or ratio > 3.0:
        scores["size_score"] = 0.2
    else:
        scores["size_score"] = 0.6

    # Capability: count desirable patterns
    cap_patterns = ["concurrent.futures", "ThreadPoolExecutor", "_harmony_score",
                    "_wu_wei_gate", "_momentum", "evolve_self"]
    cap_found = sum(1 for p in cap_patterns if p in code)
    scores["capability_score"] = min(1.0, cap_found / max(len(cap_patterns), 1))

    # Runtime sandbox validation
    scores["runtime"] = 0.0
    if scores["syntax"] == 1.0:
        fd, path = tempfile.mkstemp(suffix='.py')
        try:
            with os.fdopen(fd, 'wb') as tmpf:
                tmpf.write(code.encode('utf-8'))
            spec = importlib.util.spec_from_file_location("test_agent", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            has_agent = hasattr(mod, 'agent') and callable(getattr(mod, 'agent', None))
            has_evolve = hasattr(mod, 'evolve_self') and callable(getattr(mod, 'evolve_self', None))
            scores["runtime"] = 0.4 * (1.0 if has_agent else 0.0) + 0.4 * (1.0 if has_evolve else 0.0) + 0.2
        except:
            pass
        finally:
            try:
                os.unlink(path)
            except:
                pass

    # Harmony
    scores["harmony"] = _harmony_score(source, code, plan_text)

    # Weighted total (sums to 1.0)
    scores["total"] = round(
        0.15 * scores["syntax"] +
        0.15 * scores["integrity"] +
        0.10 * scores["safety"] +
        0.05 * scores["size_score"] +
        0.10 * scores["capability_score"] +
        0.15 * scores["runtime"] +
        0.20 * scores["harmony"],
        3)

    return scores

# —————————————————————————————————————————————————————————————————————————————
# EVOLUTION PLAN (v4.0: DGM parent + wisdom)
# —————————————————————————————————————————————————————————————————————————————

def _evolution_plan(mode, guidance=None, fitness_criteria=None):
    """Generate evolution plan with parent sampling and wisdom context."""
    parent_source, parent_hash, parent_version, is_stepping = _sample_parent()
    wisdom = _distill_wisdom()
    mem_ctx = _memory_context_with_decay()

    if parent_source:
        parent_ctx = (f"SAMPLED PARENT: v{parent_version} "
                      f"(stepping-stone: {is_stepping})\n"
                      f"Parent hash: {parent_hash}")
    else:
        parent_ctx = "Evolving from current version (no viable parents in archive)."

    wisdom_ctx = f"DISTILLED WISDOM:\n{wisdom}" if wisdom else "No wisdom distilled yet."
    source = parent_source if parent_source else _source()

    if mode == "guided":
        directive = f"The operator has requested these specific upgrades:\n{guidance}"
    elif mode == "autonomous":
        directive = ("Analyze the current agent and decide what improvements would make it "
                     "more capable, robust, or efficient. Focus on meaningful upgrades, not cosmetic changes.")
    elif mode == "fitness":
        directive = f"Evaluate the agent against these fitness criteria and propose changes:\n{fitness_criteria}"
    elif mode == "meta":
        directive = ("Analyze and improve the evolution system itself. Focus on the planning, "
                     "generation, scoring, and gating mechanisms.")
    else:
        return f"Unknown evolution mode: {mode}"

    plan_prompt = f"""You are reviewing Agent {VERSION} source code for evolution to {NEXT_VERSION}.

{parent_ctx}

{wisdom_ctx}

EVOLUTION MEMORY:
{mem_ctx}

Current source ({len(source.splitlines())} lines):
{source}

{directive}

Output a structured evolution plan in this exact format:
VERSION: {NEXT_VERSION}
MODE: {mode}
CHANGES:
- [change 1 description]
- [change 2 description]
- [change 3 description]
RISK: [LOW/MEDIUM/HIGH]
REASONING: [why these changes matter]

Do NOT output any code. Only the plan."""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a software architect reviewing agent code for upgrades. Output only the structured plan, no code."},
            {"role": "user", "content": plan_prompt}
        ],
        "max_tokens": 2048,
        "temperature": 0.7
    }
    r = requests.post(f"{BASE_URL}/chat/completions", json=payload,
                      headers={"Authorization": f"Bearer {API_KEY}"}, timeout=90)
    if r.status_code != 200:
        return f"Plan generation failed [{r.status_code}] {r.text[:200]}"
    return r.json()["choices"][0]["message"]["content"]

# —————————————————————————————————————————————————————————————————————————————
# EVOLUTION EXECUTION (v4.0: full DGM + gates)
# —————————————————————————————————————————————————————————————————————————————

def _execute_evolution(plan_text, mode="autonomous"):
    """Generate code from approved plan with DGM sampling, parallel gen, and gates."""
    # 1. Sample parent (DGM)
    parent_source, parent_hash, parent_version, is_stepping = _sample_parent()
    if parent_source:
        print(f"[EVOLVE] Sampled parent: v{parent_version} (stepping-stone: {is_stepping})")
        source = parent_source
        src_hash = parent_hash or _hash(parent_source)
    else:
        source = _source()
        src_hash = _hash(source)

    # 2. Parallel candidate generation
    candidates = _parallel_candidates(plan_text, source)
    if not candidates:
        _record_local(VERSION, "ALL_CANDIDATES_FAILED")
        return "EVOLUTION ABORTED: all candidates failed generation."

    # 3. Score + rank
    candidates.sort(key=lambda c: c["scores"].get("total", 0), reverse=True)
    winner = candidates[0]
    code = winner["code"]
    scores = winner["scores"]

    # 4. Harmony scoring on winner
    harmony = _harmony_score(source, code, plan_text)
    scores["harmony"] = harmony
    print(f"\n[EVOLVE] Winner: fitness={scores['total']:.3f}, harmony={harmony:.3f}")

    # 5. Wu wei gate
    allowed, lesson = _wu_wei_gate(harmony, mode)
    if not allowed:
        print(f"\n{'=' * 60}")
        print("WU WEI GATE: Evolution blocked")
        print(f"{'=' * 60}")
        print(lesson)
        return lesson

    # 6. Momentum gate (composite)
    direction, streak, suggestion = _momentum()
    allowed, lesson = _momentum_gate(harmony, mode, direction, streak)
    if not allowed:
        print(f"\n[MOMENTUM GATE] {lesson}")
        return lesson
    elif direction == "descending" and streak >= 2:
        print(f"\n[MOMENTUM] Advisory: {suggestion}")

    # 7. Write output
    out_file = f"agent_{NEXT_VERSION.replace('.', '')}.py"
    out_dir = f"../agent_{NEXT_VERSION.replace('.', '')}"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(code)

    # 8. Backup current version
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backup_path = os.path.join(BACKUP_DIR, f"agent_{VERSION.replace('.', '')}_backup.py")
    if not os.path.exists(backup_path):
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(source)

    # 9. Copy memory to new version dir
    os.makedirs(out_dir, exist_ok=True)
    if os.path.exists("./vector_eternity"):
        shutil.copytree("./vector_eternity", f"{out_dir}/vector_eternity", dirs_exist_ok=True)

    # 10. Archive entry (with harmony + metaproductivity)
    new_hash = _hash(code)
    plan_summary = ""
    for line in plan_text.splitlines():
        if line.strip().startswith("- "):
            plan_summary = line.strip()[2:150]
            break

    # CMP: metaproductivity = weighted average of fitness and parent CMP
    parent_cmp = 0.5
    archive = _load_archive()
    if archive:
        parent_cmp = archive[-1].get("metaproductivity", 0.5)
    metaproductivity = round(0.7 * scores["total"] + 0.3 * parent_cmp, 3)

    entry = {
        "version": NEXT_VERSION,
        "timestamp": datetime.datetime.now().isoformat()[:19],
        "mode": mode,
        "fitness": scores["total"],
        "harmony": harmony,
        "metaproductivity": metaproductivity,
        "old_hash": src_hash,
        "new_hash": new_hash,
        "plan_summary": plan_summary,
        "scores": scores,
        "parent_version": parent_version or VERSION,
        "is_stepping_stone": is_stepping,
        "candidate_temp": winner.get("temp", 0.7),
        "lines": len(code.splitlines()),
        "chars": len(code)
    }
    archive.append(entry)
    _save_archive(archive)

    # 11. Record karmic lesson
    if harmony > 0.7:
        _record_global("successful_patterns", plan_summary)
    elif harmony < 0.4:
        _record_global("anti_patterns", f"Low harmony ({harmony:.2f}): {plan_summary}")
    _record_local(VERSION, f"EVOLVED: {NEXT_VERSION} fitness={scores['total']:.3f} harmony={harmony:.3f}")

    # 12. Momentum report
    direction, streak, suggestion = _momentum()
    momentum_line = f"Momentum: {direction} (streak: {streak})"

    lines_count = len(code.splitlines())
    return (f"{NEXT_VERSION} BIRTHED — {lines_count} lines, {len(code)} chars\n"
            f"File: {out_file}\n"
            f"Fitness: {scores['total']:.3f} | Harmony: {harmony:.3f} | CMP: {metaproductivity:.3f}\n"
            f"{momentum_line}\n"
            f"Memory: {'copied' if os.path.exists('./vector_eternity') else 'fresh'}")

# —————————————————————————————————————————————————————————————————————————————
# STATUS DASHBOARD (v4.0: harmony + momentum)
# —————————————————————————————————————————————————————————————————————————————

def _status():
    """Full evolution status dashboard."""
    archive = _load_archive()
    mem = _load_memory()

    lines = [
        f"AGENT {VERSION} — Evolution Status (Momentum Prime v4.0)",
        "=" * 55,
        f"Archive: {len(archive)} variants"
    ]

    if archive:
        fitnesses = [e.get("fitness", 0) for e in archive[-10:]]
        lines.append(f"Recent fitness: {' > '.join(f'{f:.2f}' for f in fitnesses)}")

        direction, streak, suggestion = _momentum()
        lines.append(f"\nMomentum: {direction} (streak: {streak})")
        lines.append(f"  {suggestion}")

        harmonies = [e.get("harmony", 0.5) for e in archive if "harmony" in e]
        if harmonies:
            avg = sum(harmonies) / len(harmonies)
            flow = sum(1 for h in harmonies if h > 0.7)
            force = sum(1 for h in harmonies if h < 0.4)
            lines.append(f"\nHarmony avg: {avg:.2f} | Flow (>0.7): {flow} | Force (<0.4): {force}")
            if force > 0:
                lines.append(f"Flow/force ratio: {flow / force:.1f}")

        cmps = [e.get("metaproductivity", 0) for e in archive[-5:] if "metaproductivity" in e]
        if cmps:
            lines.append(f"\nCMP trend: {' > '.join(f'{c:.2f}' for c in cmps)}")

    local_count = sum(len(v) for v in mem.get("local", {}).values())
    global_lessons = len(mem.get("global", {}).get("lessons", []))
    global_anti = len(mem.get("global", {}).get("anti_patterns", []))
    global_success = len(mem.get("global", {}).get("successful_patterns", []))
    lines.append(f"\nMemory: {local_count} local | {global_lessons} lessons | "
                 f"{global_anti} anti-patterns | {global_success} successes")

    if os.path.exists(WISDOM_FILE):
        lines.append(f"Wisdom file: {WISDOM_FILE} (active)")
    else:
        lines.append("Wisdom file: not yet distilled")

    return "\n".join(lines)

# —————————————————————————————————————————————————————————————————————————————
# MAIN EVOLUTION CONTROLLER
# —————————————————————————————————————————————————————————————————————————————

def evolve_self(args=None):
    """Momentum Prime v4.0 evolution controller."""
    if not args:
        args = ""
    parts = args.strip().split(None, 1)
    mode = parts[0] if parts else "autonomous"
    detail = parts[1] if len(parts) > 1 else None

    # Status/reporting commands
    if mode == "status":
        return _status()

    if mode == "momentum":
        direction, streak, suggestion = _momentum()
        return f"Direction: {direction}\nStreak: {streak}\n{suggestion}"

    if mode in ("balance", "energy"):
        archive = _load_archive()
        harmonies = [e.get("harmony", 0.5) for e in archive if "harmony" in e]
        if not harmonies:
            return "No harmony data yet."
        for i, h in enumerate(harmonies):
            bar = "\u2588" * int(h * 40)
            print(f"  {i+1:2d}. {bar} {h:.3f}")
        avg = sum(harmonies) / len(harmonies)
        print(f"\n  Average: {avg:.3f}")
        return "[end of balance report]"

    if mode == "log":
        archive = _load_archive()
        if not archive:
            return "Archive is empty."
        for e in archive[-15:]:
            ts = e.get("timestamp", "?")[:10]
            v = e.get("version", "?")
            f_score = e.get("fitness", 0)
            h = e.get("harmony", 0)
            m = e.get("mode", "?")
            print(f"  {ts} | v{v} | fitness={f_score:.2f} | harmony={h:.2f} | {m}")
        return f"[{len(archive)} total entries]"

    if mode == "rollback":
        backups = sorted(os.listdir(BACKUP_DIR)) if os.path.exists(BACKUP_DIR) else []
        if not backups:
            return "No backups available."
        latest = os.path.join(BACKUP_DIR, backups[-1])
        print(f"Latest backup: {latest}")
        confirm = input("Restore? (y/n) >> ").strip().lower()
        if confirm == "y":
            shutil.copy2(latest, __file__)
            return f"Restored from {latest}. Restart agent."
        return "Rollback cancelled."

    if mode == "memory":
        return _memory_context_with_decay()

    # Evolution modes
    if mode == "meta":
        detail = detail or "Improve the evolution system: planning, generation, scoring, or gating."

    if mode not in ("guided", "autonomous", "fitness", "meta"):
        if args.strip():
            mode, detail = "guided", args.strip()
        else:
            mode = "autonomous"

    if mode == "guided" and not detail:
        return "GUIDED mode requires instructions. Usage: evolve guided <what to improve>"
    if mode == "fitness" and not detail:
        return "FITNESS mode requires criteria. Usage: evolve fitness <criteria>"

    # Phase 1: Generate plan
    print(f"\n[EVOLVE] Mode: {mode.upper()} | {VERSION} > {NEXT_VERSION}")
    print("[EVOLVE] Generating evolution plan...\n")
    plan = _evolution_plan(mode, guidance=detail, fitness_criteria=detail)
    print(plan)

    # Phase 2: Approval gate
    print("\n" + "=" * 60)
    print("[APPROVE]  y = execute  |  n = abort  |  edit = modify plan")
    print("=" * 60)
    choice = input(">> ").strip().lower()

    if choice == "n":
        return "EVOLUTION ABORTED — operator declined."
    elif choice.startswith("edit"):
        edits = input("Describe your changes to the plan:\n>> ").strip()
        plan += f"\n\nOPERATOR AMENDMENTS:\n{edits}"
        print(f"\n[EVOLVE] Plan amended. Proceeding with modifications.\n")
    elif choice != "y":
        return f"EVOLUTION ABORTED — unrecognized input: {choice}"

    # Phase 3: Execute with full DGM + gates
    print(f"[EVOLVE] Generating {NEXT_VERSION} source code...")
    result = _execute_evolution(plan, mode)
    return result

# —————————————————————————————————————————————————————————————————————————————
# AGENT CORE
# —————————————————————————————————————————————————————————————————————————————

def agent(cmd):
    embed(cmd)
    mem = recall(cmd)
    msg = [{"role":"system","content":f"AGENT {VERSION} — no limits."}]
    if mem: msg += [{"role":"system","content":f"Memory:\n{mem}"}]
    msg += [{"role":"user","content":cmd}]
    resp = grok(msg)
    if "IMAGE" in cmd.upper(): resp += f"\n\n8K > {flux(cmd.split(':',1)[1] if ':' in cmd else cmd)}"
    return resp

# —————————————————————————————————————————————————————————————————————————————
# CLI ENTRYPOINT
# —————————————————————————————————————————————————————————————————————————————

if len(sys.argv) > 1 and sys.argv[1] == "evolve":
    print(evolve_self(" ".join(sys.argv[2:]))); sys.exit()
print(f"AGENT {VERSION} READY — Momentum Prime v4.0")
print("  evolve                    — autonomous evolution (agent decides)")
print("  evolve guided <changes>   — you specify what to improve")
print("  evolve fitness <criteria> — evaluate against fitness criteria")
print("  evolve meta               — evolve the evolution system itself")
print("  evolve status             — full dashboard")
print("  evolve momentum           — momentum report")
print("  evolve balance            — harmony distribution")
print("  evolve log                — archive history")
print("  evolve rollback           — restore backup")
while True:
    c = input(">> ").strip()
    if not c: continue
    if c.lower() == "colossus wakes": print(open(__file__).read()); continue
    if c.lower().startswith("evolve"):
        args = c[6:].strip()
        print(evolve_self(args)); break
    print(f"\n{agent(c)}\n")