## Installere verktøy
- Med uv:
```bash
uv sync --extra docs
```

## Kjøre dokumentasjon lokalt
```bash
uv run --extra docs mkdocs serve -a 0.0.0.0:8000
```
Dokumentasjonen kjører nå på `http://127.0.0.1:8000` i prosjektets virtuelle miljø

## Bygg statisk side
```bash
uv run --extra docs mkdocs build
```
Skriver til `site/`.

## Deploy
Siten publiseres med GitHub Pages (`pages` workflow).