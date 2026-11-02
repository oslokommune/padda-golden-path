---
name: padda-golden-path
description: Padda golden-path assistant for Databricks data engineering in Oslo kommune. Use whenever the user wants to create a new Databricks Asset Bundle, data pipeline, ingestion job, or data product on the Padda platform, or asks how to structure bronze/silver/gold tables, Auto Loader ingestion, data quality checks (expectations/DQX), bundle naming, deploy targets, cost tags, or dataproduct.yaml metadata — even if they never mention "golden path" or this skill by name. Scaffolds new bundles from the official golden-path template and applies platform conventions when reviewing or writing pipeline code.
allowed-tools:
  - Bash(curl -sL https://raw.githubusercontent.com/oslokommune/padda-golden-path/*)
---

# Padda golden path

The Padda documentation is the source of truth for how to build on the platform. This
skill does not repeat it: it tells you which pages to read for a request, how to read
them, and the few things the pages do not say.

## Steps

1. **Identify the phase** of the request in the page map below. A request may span
   several phases; take each one it touches.
2. **Fetch the pages**: every required page of each phase, every conditional page whose
   condition matches the request, and nothing else. Read each page with

   ```bash
   curl -sL https://raw.githubusercontent.com/oslokommune/padda-golden-path/main/docs/<path>.md
   ```

   Never use WebFetch for the docs: it returns a summary and drops the code blocks. This
   step is done when every one of those pages is fetched, before you write code or
   answer.
3. **Apply what the pages say.** Where the pages are silent, see "Precedence".
4. **End the reply with one line of sources**: the pages you relied on, as
   `https://padda.data.oslo.systems/<path>/` links.

## Page map

Paths are under `docs/`, without `.md`.

| Phase | Required | Conditional |
|---|---|---|
| Every phase | `referanse/navnekonvensjoner` | |
| Scaffold a bundle | `guider/utvikle-og-deploye/ta-i-bruk-bundles`, plus the template schema (see "Scaffolding") | |
| Land and ingest to bronze | `guider/hente-inn-data/auto-loader` | `guider/hente-inn-data/laste-opp-til-landing-zone` (files), `guider/hente-inn-data/hente-data-via-api` (API source), `referanse/landing-zone` |
| Silver | `guider/bearbeide-data/skrive-transformasjoner` | `guider/bearbeide-data/deduplisere-data` (dedup), `guider/bearbeide-data/haandtere-ugyldige-rader` (a cast can fail) |
| Gold and data product | `guider/dele-og-hente-ut/dokumentere-dataprodukt` | `referanse/dataprodukt` |
| Deploy | `guider/utvikle-og-deploye/deploye-til-produksjon` | `guider/utvikle-og-deploye/haandtere-secrets` (secrets), `referanse/databricks-bundles` |
| Monitor | | `guider/overvaake-og-drifte/slack-varsler`, `guider/overvaake-og-drifte/ferskhetsvarsel`, `guider/overvaake-og-drifte/bruke-dqx` (each when asked), `referanse/varsling-og-alarmer` |
| Any new job or pipeline | | `guider/overvaake-og-drifte/kostnadstagging` |
| Concept questions | | the `om-plattformen/konsepter/` page the `nav` names for the topic |

For anything outside this map, or a page that returns 404, read the `nav` in
`zensical.toml`, which lists every page:

```bash
curl -sL https://raw.githubusercontent.com/oslokommune/padda-golden-path/main/zensical.toml
```

## Scaffolding

Create a new bundle from the golden-path template on GitHub:

```bash
databricks bundle init https://github.com/oslokommune/padda-golden-path --template-dir bundle-templates
```

A non-interactive shell never prompts, so every answer goes in a JSON file passed with
`--config-file <file>`. The prompt names and allowed values are in the template schema:

```bash
curl -sL https://raw.githubusercontent.com/oslokommune/padda-golden-path/main/bundle-templates/databricks_template_schema.json
```

Read the template from GitHub only for scaffolding; for everything else, read the docs.

## Precedence

The docs win. Where they are silent, follow the patterns in the bundle's own generated
files (`tests/`, `pyproject.toml`, existing jobs and pipelines), then Databricks'
documentation. Say which of these you used.
