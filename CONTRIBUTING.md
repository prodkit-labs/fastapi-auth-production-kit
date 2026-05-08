# Contributing

This repo is designed as a practical production kit.

Good contributions:

- Keep the local path runnable without paid services.
- Add tests for behavior changes.
- Keep provider docs scenario-specific and tradeoff-aware.
- Avoid absolute provider claims.
- Keep commercial links out of install commands and README hero sections.

Run checks before opening a PR:

```bash
ruff check .
pytest
```
