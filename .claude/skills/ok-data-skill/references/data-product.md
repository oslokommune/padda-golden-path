# Data product thinking (Padda)

Source of truth: `docs/referanse/dataprodukt.md` (RFC status — expect evolution) and
`docs/om-plattformen/konsepter/dataprodukter.md`.

## What makes a dataset a data product

A gold table becomes a **data product** when consumers outside the producing team
depend on it. A data product must be:

- **Owned** — a named owner close to the source domain, accountable for it.
- **Documented** — purpose, contents, and quality understandable without asking.
- **Findable and reusable** — discoverable in the catalog, usable without tribal
  knowledge.
- **Reliable** — updated as promised, with known quality.

Internal pipelines and intermediate tables do not need product metadata — but the
moment a gold table gets an external consumer, it does. Raise this with users who are
about to share tables ad hoc.

## Metadata model

Primary operational format is **ODPS** (Open Data Product Specification,
metadata-as-code); output-port contracts use **ODCS**. Export/interop targets DCAT-AP-NO
v3 / DPROD. The machine-readable form is a `dataproduct.yaml` in the bundle root
(template: `assets/dataproduct.yaml` in this skill).

Required (SKAL) fields:

| Field | Meaning |
|-------|---------|
| `id` | Stable identity — never reused, survives renames |
| `name`, `title`, `description`, `purpose` | What it is and why it exists |
| `domain` | Business domain it belongs to |
| `owner` | Dataprodukteier — accountable, decides direction |
| `dataSteward` | Dataforvalter — day-to-day quality and documentation |
| `technicalOwner` | Teknisk eier — pipelines, infra, incidents |
| `lifecycleStatus` | See lifecycle below |
| `assets` | The underlying tables/views (hierarchy: System → Database → Table → Datasett) |
| `outputPorts` | ≥ 1 — how consumers actually get the data (UC table/view, Delta Sharing, API) |
| `accessPolicy` | How access is requested and granted |
| `usageRights` | What consumers may do after access is granted |
| `classification` | Sensitivity: green (public) / yellow (internal) / red (confidential) |
| `version` | Product version |

**accessPolicy vs usageRights is a deliberate distinction**: accessPolicy answers "how
do I get in?", usageRights answers "what may I do once I'm in?". Do not merge them.

## Lifecycle

```
draft → development → published → deprecated → retired
```

New scaffolds start at `draft`. `published` is a promise to consumers — from then on,
breaking changes must be documented and should be handled via a new major version, a
new output port, and/or a notice period. Deprecation before retirement gives consumers
time to migrate.

## Practical guidance when helping developers

- When scaffolding (`ok data init`), ask whether the bundle will produce a data
  product. If yes, generate `dataproduct.yaml` from the template and fill in what the
  user knows; leave unknown fields as explicit `TODO` rather than guessing. Set
  `lifecycleStatus: draft`.
- The three roles may be the same person in a small team — that is fine, but all three
  must be named. Push back gently on `owner: <team-alias>` with no person behind it.
- Classification drives everything downstream (landing-zone prefix, access policy,
  sharing). If the user is unsure, yellow (internal) is the safe interim default —
  never assume green.
- Version and document breaking changes: renamed/removed columns, changed semantics,
  changed update cadence. Additive changes (new columns) are normally non-breaking.
- In Databricks terms: output ports map to UC tables/views/volumes or Delta Sharing;
  classification and ownership map to UC tags and grants.
