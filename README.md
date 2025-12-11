# padda-golden-path

Golden paths for padda, dataplattformen for data engineers i Oslo kommune.

## Dokumentasjon (MkDocs)

Ligger i `docs/` og er konfigurert via `mkdocs.yml`.
For mer informasjon gå til egen [readme](./docs/README.md).
Gå til [oslokommune.github.io/padda-golden-path](https://oslokommune.github.io/padda-golden-path) for offisiell dokumentasjon av Padda.

## Linting (Ruff)

Installer pre-commit hooks (valgfritt, men anbefalt):
```bash
uvx pre-commit install
```

Kjør Ruff lokalt:
```bash
uvx ruff check . --fix
uvx ruff format .
```

## Test

Testene kjøres med pytest:
```bash
uv run pytest
```

For coverage-rapport:
```bash
uv run pytest --cov=libs
```
