## Installere verktøy
Med uv:
```bash
uv sync --extra docs
```

## Kjøre dokumentasjon lokalt
```bash
uv run --extra docs zensical serve
```
Dokumentasjonen kjører nå på `http://localhost:8000` i prosjektets virtuelle miljø

## Bygg statisk side
```bash
uv run --extra docs zensical build
```
Skriver til `site/`.

## Deploy
Siten publiseres med GitHub Pages (`pages` workflow).
