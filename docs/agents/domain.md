# Domain Docs

How engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- `GLOSSARY.md` at the repo root.
- `docs/adr/`: read ADRs that touch the area you're about to work in.

This repo uses a single-context layout. Do not require or create `GLOSSARY-MAP.md` or context-scoped ADR directories.

## File structure

```text
/
├── GLOSSARY.md
├── docs/adr/
└── src/
```

If these files don't exist, proceed silently. Don't flag their absence or suggest creating them upfront.

## Use the glossary's vocabulary

When output names a domain concept, use the term as defined in `GLOSSARY.md`. Don't drift to synonyms the glossary explicitly avoids.

If a needed concept is not in the glossary, consider whether it is missing domain language or existing project terminology. `/domain-modeling` can resolve glossary gaps lazily.

## Flag ADR conflicts

If output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders), but worth reopening because…_
