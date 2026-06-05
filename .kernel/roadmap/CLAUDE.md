# .kernel Roadmap

This roadmap tracks improvements to the `ai-project-2ndbrain` template repo itself — not the project it's used for.

Items here are about the template: setup.sh improvements, new vault structure ideas, CLAUDE.md enhancements, documentation updates, etc.

## Roadmap item lifecycle

**When writing a new roadmap item spec**, include a `## Test Plan` section before any implementation starts. It should list:
- What mechanics can be tested (new config fields, new files, new parsing logic, new skill behavior)
- What the expected inputs and outputs are
- What edge cases matter

This forces the feature to be concrete before a single line changes, and directly informs what gets added to `.kernel/test.py`.

**When implementing a roadmap item**, run the test suite first (baseline) and again after (verify):

```bash
python3 .kernel/test.py
```

All tests must pass before marking the item as done. New features must ship with new tests — no closing an item without covering its mechanics in `.kernel/test.py`.
