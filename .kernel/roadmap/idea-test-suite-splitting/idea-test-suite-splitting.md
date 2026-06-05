---
status: idea
priority: low
owner: ""
phase: ""
depends_on: []
---

# Idea: Split test.py into multiple focused test files

## One-Line Overview

As `.kernel/test.py` grows with each new feature, it may make sense to split it into focused files (e.g. `test_onboard.py`, `test_bootstrap.py`) with a runner that executes all of them.

## What's the idea

Right now everything lives in one `test.py`. That works fine at small scale. As more roadmap items ship and each adds tests, the file could become hard to navigate and slow to run when you only care about one skill.

Possible split:
- `test_onboard.py` — repo structure, config, sow.config.yaml, placeholder replacement, branch naming
- `test_bootstrap.py` — bootstrap state, filter logic, inbox file format, Drive/Slack integration
- `test_structure.py` — gitignore, required files, template completeness
- A top-level runner (`test.py`) that just calls all of them: `python3 .kernel/test.py`

## When to revisit

When `test.py` exceeds ~400 lines or when running the full suite takes long enough to be annoying. Until then, one file is simpler.
