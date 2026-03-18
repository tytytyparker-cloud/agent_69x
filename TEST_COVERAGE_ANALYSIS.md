# Test Coverage Analysis — Agent 6.91

## Current State

**Test coverage: 0%.** The project has no tests, no test framework, no coverage tooling, and no CI/CD pipeline to run them.

The entire application lives in a single 57-line file (`agent_69x.py`) with 6 functions and a top-level main loop.

---

## Functions and Their Testability

| Function | Lines | External Deps | Testability |
|----------|-------|---------------|-------------|
| `embed(t)` | 1 | ChromaDB | Easy (mock ChromaDB) |
| `recall(p)` | 1 | ChromaDB | Easy (mock ChromaDB) |
| `grok(m)` | 4 | x.ai HTTP API | Medium (mock requests) |
| `flux(prompt)` | 3 | x.ai HTTP API | Medium (mock requests) |
| `evolve_self()` | 7 | grok + filesystem | Medium (mock grok + tmpdir) |
| `agent(cmd)` | 8 | embed, recall, grok, flux | Medium (mock sub-functions) |

---

## Recommended Test Plan

### Priority 1 — Unit tests for core logic

These tests would catch regressions in the most important behavior with minimal effort.

**1. `grok()` — message construction and API handling**
- Verify correct HTTP request payload (model, temperature, max_tokens)
- Verify temperature switches to 2.0 when "DEFY" appears in messages
- Verify it returns the response content on HTTP 200
- Verify it returns `"API bleed"` on non-200 status codes
- Verify timeout is set to 60s

**2. `flux()` — image generation API handling**
- Verify correct payload (model, prompt, size, steps, guidance_scale)
- Verify it extracts and returns the image URL on success
- Verify it returns `"Flux denied"` on failure
- Verify timeout is set to 90s

**3. `agent()` — command orchestration**
- Verify it calls `embed()` with the command
- Verify it calls `recall()` and injects memory into the system message when memory exists
- Verify it skips memory injection when `recall()` returns empty
- Verify it appends the Flux image URL when the command contains "IMAGE"
- Verify `IMAGE:` prefix splitting works correctly

### Priority 2 — Vector memory round-trip

**4. `embed()` + `recall()`**
- Verify a stored document can be recalled by a semantically similar query
- Verify `recall()` returns empty string when the collection is empty
- These can use a real in-memory ChromaDB client (no mock needed)

### Priority 3 — Self-evolution and edge cases

**5. `evolve_self()`**
- Verify it writes the generated code to `agent_692.py`
- Verify it copies `vector_eternity/` to `../agent_692/`
- Verify it returns the expected status string
- Use a temporary directory to avoid filesystem side effects

**6. Input parsing edge cases**
- `"colossus wakes"` backdoor path
- `"evolve"` / `"evolve self"` commands
- `sys.argv` evolve trigger
- `IMAGE:` with and without a colon

---

## Recommended Tooling Setup

```
# pyproject.toml (minimal)
[project]
name = "agent-69x"
requires-python = ">=3.9"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.coverage.run]
source = ["."]
omit = ["tests/*"]
```

**Framework:** `pytest` + `pytest-cov` for coverage, `unittest.mock` for mocking HTTP calls and ChromaDB.

**Run command:** `pytest --cov --cov-report=term-missing`

---

## Structural Recommendations

1. **Extract configuration constants** (`API_KEY`, `BASE_URL`, `MODEL`, `FLUX`) into a config dict or dataclass so tests can override them without monkeypatching module globals.

2. **Guard the main loop** behind `if __name__ == "__main__":` so importing `agent_69x` for testing doesn't trigger the REPL loop or ChromaDB initialization at import time. This is the single biggest blocker for testability today.

3. **Inject the ChromaDB collection** instead of creating it at module scope. A function like `create_collection(path)` would let tests pass a temporary directory.

4. **Add a GitHub Actions workflow** (`.github/workflows/test.yml`) to run `pytest` on every push/PR and enforce a minimum coverage threshold.

---

## Summary

| Area | Risk | Effort | Priority |
|------|------|--------|----------|
| `grok()` / `flux()` API handling | High — silent failures | Low | P1 |
| `agent()` orchestration | High — core feature | Low | P1 |
| Vector memory round-trip | Medium | Low | P2 |
| `evolve_self()` filesystem ops | Medium — destructive | Medium | P3 |
| `if __name__` guard (testability) | Blocker for all tests | Trivial | P0 |

The most impactful first step is adding the `if __name__ == "__main__":` guard and a single test file that mocks `requests.post` to validate `grok()` and `flux()` behavior. This alone would cover the highest-risk code paths with minimal effort.
