## Installere verktøy
Med uv:
```bash
uv sync --extra docs
```

## Kjøre dokumentasjon lokalt
```bash
uv run --extra docs mkdocs serve -a 0.0.0.0:8000
```
Dokumentasjonen kjører nå på `http://127.0.0.1:8000` i prosjektets virtuelle miljø.

## Notion-sider
Notion-innhold hentes automatisk under bygg dersom:

1. `NOTION_API_TOKEN` er satt (1Password/`op run --env-file ...` anbefales).
2. `NOTION_PAGE_IDS` settes til kommaseparerte page IDs.
3. Kjør `uv run --extra docs mkdocs build` eller `mkdocs serve` med variablene; sider lagres i `docs/notion/` og [navigasjonsmenyen](notion) oppdateres.

## Bygg statisk side
```bash
uv run --extra docs mkdocs build
```
Skriver til `site/`.

## Deploy
Siten publiseres med GitHub Pages (`pages` workflow).
