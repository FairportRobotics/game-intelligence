# Engineering Standards

## Development Workflow

- Use test-driven development with one red-green cycle at a time.
- Write the public-seam test first and confirm it fails before adding implementation.
- Add only the implementation needed to make the current test pass.
- Repeat for the next behavior; avoid bulk implementation or speculative features.
- Refactor only after green tests, and rerun the relevant checks after each refactor.

## Module Design

- Design deep modules with a small public interface that hides substantial behavior.
- Place tests at public seams, not against private methods or internal collaborators.
- Prefer one vertical slice across the module over horizontal implementation layers.
- Keep adapters at system seams such as external APIs, databases, time, randomness, and the file system.
- Keep domain behavior independent of framework and source-specific formats.
- Pass dependencies into modules instead of constructing external collaborators internally.
- Do not mock internal modules or assert internal call counts.
- Tests must verify observable behavior and use independent, literal expected values.

## Testing

- Use pytest for automated tests.
- Run the complete test suite before considering implementation complete:

  ```bash
  ./.venv/bin/python -m pytest
  ```

- Keep tests deterministic and isolated.
- Test behavior through public interfaces and real local infrastructure when practical.
- Mock only external system boundaries.
- One test should verify one logical behavior.
- Test names should describe the capability or user-visible behavior under test.

## Python Type Checking

- Type-check Python source and tests with Pyrefly.
- Run Pyrefly before implementation is complete:

  ```bash
  ./.venv/bin/pyrefly check
  ```

- Public module interfaces must include type annotations for parameters and return values.
- Domain data should use concrete types rather than untyped dictionaries or `Any` once a stable shape is known.
- Dataclasses or typed structures are preferred for canonical domain records.
- Pyrefly project settings may be added through `pyrefly.toml` or `pyproject.toml`, and all Pyrefly diagnostics must be resolved before completion.
- `Any`, casts, and ignores require a specific justification and should be avoided at public interfaces.

## Python Style and Linting

- Lint Python source and tests with Ruff.
- Run Ruff before implementation is complete:

  ```bash
  ./.venv/bin/python -m ruff check .
  ```

- Format Python source and tests with Ruff when formatting is available:

  ```bash
  ./.venv/bin/python -m ruff format .
  ```

- Follow existing repository naming and formatting conventions.
- Do not disable lint rules unless the specific case is documented and necessary.

## Completion Checks

A change is complete only when all of the following pass:

- Red-green TDD evidence for the behavior changed.
- The full pytest suite.
- Ruff linting.
- Python type checking.
- The pull-request CI workflow, which runs pytest, Pyrefly, and Ruff.
- After code changes, update the Graphify graph with `./.venv/bin/graphify update .`.
- A review for public-interface depth and unnecessary cross-module seams.

## Commits

- Keep commits small and focused on one coherent behavior or change.
- Write commit messages that document the intent and user-visible outcome of the code change.
- Include relevant validation results in the commit description when they help explain the outcome.
