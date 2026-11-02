---
name: padda-golden-path
description: Padda golden-path assistant for Databricks data engineering in Oslo kommune. Use whenever the user wants to create a Databricks Asset Bundle, pipeline, job, ingestion (Auto Loader, landing zone, API source) or data product on the Padda platform, or asks how to structure bronze/silver/gold tables, data quality checks (expectations/DQX), naming, cost tags, secrets, deploy targets, GitHub Actions deploys, Slack or freshness alerts, or dataproduct.yaml metadata — even if they never mention "golden path" or this skill by name. Scaffolds new bundles from the official template and applies platform conventions when reviewing or writing pipeline code.
compatibility: Requires curl and network access to raw.githubusercontent.com; scaffolding also needs the Databricks CLI.
allowed-tools: Bash(curl -sL https://raw.githubusercontent.com/oslokommune/padda-golden-path/*)
---

# Padda golden path

The Padda documentation is the source of truth for how to build on the platform. This
skill does not repeat it: it tells you which pages to read for a request, how to read
them, and the few things the pages do not say.

## Steps

1. **Identify the phase** of the request in the page map below. A request may span
   several phases; take each one it touches.
2. **Fetch the `nav`, then the pages.** The `nav` in `zensical.toml` lists every page the
   docs have today; the map below is a reading order and may lag behind it:

   ```bash
   curl -sL https://raw.githubusercontent.com/oslokommune/padda-golden-path/main/zensical.toml
   ```

   Fetch every required page of each phase, every conditional page whose condition
   matches the request, and every page the `nav` lists in the phase's section or under
   `Referanse` whose title matches the request but the map does not name; nothing else.
   Read each page with its own call:

   ```bash
   curl -sL https://raw.githubusercontent.com/oslokommune/padda-golden-path/main/docs/<path>.md
   ```

   Read the docs with `curl`, not a web-fetch or browse tool: those often return a summary
   and drop the code blocks. One page per call keeps each page within the tool's output
   limit; if the tool saved an output to a file instead of showing it, read that file.
   This step is done when every one of those pages is fetched, before you write code or
   answer.
3. **Apply what the pages say**: done when every rule the fetched pages state for the
   request is reflected in your output. Where the pages are silent, see "Precedence".
4. **End the reply with one line of sources**: the pages you relied on, as
   `https://padda.data.oslo.systems/<path>/` links.

## Page map

Paths are under `docs/`, without `.md`. Phases follow the `Guider` sections of the `nav`:
Utvikle og deploye (scaffold, deploy), Hente inn data (bronze), Bearbeide data (silver),
Dele og hente ut data (gold), Overvåke og drifte (monitor).

| Phase | Required | Conditional |
|---|---|---|
| Every phase | `referanse/navnekonvensjoner` | |
| Scaffold a bundle | `guider/utvikle-og-deploye/ta-i-bruk-bundles`, plus the template schema (see "Scaffolding") | |
| Land and ingest to bronze | `guider/hente-inn-data/auto-loader` | `guider/hente-inn-data/laste-opp-til-landing-zone` (files), `guider/hente-inn-data/hente-data-via-api` and `referanse/sam-deploy` (API source), `referanse/landing-zone` |
| Silver | `guider/bearbeide-data/skrive-transformasjoner` | `guider/bearbeide-data/deduplisere-data` (dedup), `guider/bearbeide-data/haandtere-ugyldige-rader` (a cast can fail), `referanse/datakvalitet` (expectations or constraints) |
| Gold and data product | `guider/dele-og-hente-ut/dokumentere-dataprodukt` | `referanse/dataprodukt` |
| Deploy | `guider/utvikle-og-deploye/deploye-til-produksjon` | `guider/utvikle-og-deploye/haandtere-secrets` (secrets), `referanse/databricks-bundles` |
| Monitor | | `guider/overvaake-og-drifte/slack-varsler`, `guider/overvaake-og-drifte/ferskhetsvarsel`, `guider/overvaake-og-drifte/bruke-dqx` (each when asked), `referanse/varsling-og-alarmer` |
| Any new job or pipeline | | `guider/overvaake-og-drifte/kostnadstagging` |
| Concept questions | | the `om-plattformen/konsepter/` page the `nav` names for the topic |

A `nav` section with no phase here, or a page the map does not name, is newer than this
skill: read it when its title matches the request, and say in the reply that the skill
needs an update. A page that returns `404: Not Found` has moved: take its current path
from the `nav`.

A fetch that returns nothing at all is a page you have not read: say so and ask before
continuing, since the conventions exist only in the docs.

## Scaffolding

Create a new bundle from the golden-path template on GitHub:

```bash
databricks bundle init https://github.com/oslokommune/padda-golden-path --template-dir bundle-templates
```

This replaces the local-path command and the cloned-repo prerequisite on the
`ta-i-bruk-bundles` page: developers have no checkout of `padda-golden-path`. The CLI may
suggest `databricks aitools install`; that is Databricks' own skill set, separate from
scaffolding, and the docs remain the source of conventions.

A non-interactive shell never prompts, so every answer goes in a JSON file passed with
`--config-file <file>`. The prompt names and allowed values are in the template schema:

```bash
curl -sL https://raw.githubusercontent.com/oslokommune/padda-golden-path/main/bundle-templates/databricks_template_schema.json
```

Read the template from GitHub only for scaffolding; for everything else, read the docs.

## Precedence

The docs win, except where "Scaffolding" says otherwise. Where the docs are silent, follow
the patterns in the bundle's own generated files (`tests/`, `pyproject.toml`, existing jobs
and pipelines), then Databricks' documentation. Say which of these you used.
