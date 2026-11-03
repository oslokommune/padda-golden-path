# Medallion architecture and Spark patterns (Padda)

Source of truth: `docs/om-plattformen/konsepter/klassifisering-datakvalitet.md`,
`docs/guider/hente-inn-data/auto-loader.md`, `docs/referanse/datakvalitet.md`,
`docs/referanse/lagring-og-ytelse.md`, `docs/kom-i-gang/din-forste-datapipeline.md`.

## The layers

```
Landing zone (S3) → bronze → silver → gold
```

Default schema names per catalog: `bronze_default`, `silver_default`, `gold_default`.
Three layers are the recommendation, not a mandate — a trivial source may skip silver,
a complex domain may need more steps. The rationale for layering: reproducibility
(bronze preserves the raw truth), traceability, independent re-runnable steps, and
reuse (several gold products from one silver table).

### Landing zone

- One S3 bucket per workspace. Data arrives via a **sender** (logical source identity)
  provisioned by the platform team in `padda-iac`.
- Each sender gets IAM users and S3 prefixes per confidentiality level:
  `s3://<bucket>/<sender>/green/` (public), `yellow/` (internal), `red/` (confidential).
  Never mix levels in one prefix.
- Preferred file formats: Parquet, then ndjson, then CSV (UTF-8). Organize
  incrementally by date: `.../green/2026/02/17/data-001.parquet`.

### Bronze — raw, faithful, append-only

- Mirror the source. No dedup, no renames, no business logic.
- Columns typically land as `STRING` (`inferColumnTypes => false`) so ingestion never
  fails on a bad value — type casting is silver's job, where failures are visible and
  fixable.
- Always add ingestion metadata columns:

```sql
SELECT
  *,
  _metadata.file_path AS source_file_path,
  _metadata.file_modification_time AS source_file_modified_at,
  current_timestamp() AS ingested_at
FROM STREAM read_files(...)
```

### Silver — cleaned and standardized

- `snake_case` column names, correct data types, `NOT NULL` where the domain requires
  it, deduplication, expectations, defined primary/secondary keys. Aim for third
  normal form.

### Gold — business-ready data products

- Joins, aggregations, business logic. Gold tables are the data products consumed by
  BI (Power BI via SQL Warehouse) and other teams. Every gold table needs an owner —
  see `references/data-product.md`.

## Ingestion: Auto Loader via Declarative Pipelines

The golden path for file ingestion is a Declarative Pipeline reading from the landing
zone with `read_files()` (Auto Loader). Two reference bundles exist in the
`padda-databrikker` repo (`bundles/autoloader_permissive`, `bundles/autoloader_strict`)
— copy one as a starting point rather than writing from scratch.

Choose by data-quality posture (mix and match in practice):

| | Permissive | Strict |
|---|---|---|
| New column in source | Auto-added to bronze (`schemaEvolutionMode => 'addNewColumns'`) | Pipeline fails (`failOnNewColumns`) |
| Invalid/corrupt row | Passes into bronze | Pipeline fails (`mode => 'FAILFAST'`, explicit `schema`) |
| Fits | A bad row here and there is acceptable | No data is better than wrong data |

Permissive bronze table:

```sql
CREATE OR REFRESH STREAMING TABLE ${catalog}.bronze_default.my_table AS
SELECT *,
  _metadata.file_path AS source_file_path,
  _metadata.file_modification_time AS source_file_modified_at,
  current_timestamp() AS ingested_at
FROM STREAM read_files(
  's3://<landing-zone-bucket>/<sender>/green/*.json',
  format => "json",
  schemaEvolutionMode => 'addNewColumns',
  inferColumnTypes => false
);
```

Strict variant: declare all expected columns `NOT NULL` in the `CREATE ... TABLE`
column list, pass an explicit `schema =>`, `mode => 'FAILFAST'`,
`schemaEvolutionMode => 'failOnNewColumns'`.

Python Auto Loader (for jobs rather than declarative pipelines) uses
`spark.readStream.format("cloudFiles")` with `cloudFiles.schemaLocation` and a
`checkpointLocation` on the writer — both required for incremental, exactly-once
pickup of new files.

Pipelines run serverless by default (`serverless: true`, `photon: true` in the
pipeline resource). Daily scheduled trigger is the normal cadence.

## Data quality

Three mechanisms, in order of reach:

1. **Delta constraints** (any Delta table): `NOT NULL`, `CHECK` — strictly enforced on
   write. `PRIMARY KEY`/`FOREIGN KEY` are informational only, not enforced.
2. **Expectations** (Declarative Pipelines): `EXPECT` with modes `WARN` (default),
   `DROP ROW`, `FAIL UPDATE`. Use on silver to quarantine or stop bad data.
3. **DQX** (Databricks Labs framework) for richer dataset-level checks — uniqueness,
   freshness, foreign-key consistency, aggregate comparisons:

```python
from databricks.labs.dqx.engine import DQEngine
from databricks.labs.dqx import check_funcs
from databricks.labs.dqx.rule import DQDatasetRule
from databricks.sdk import WorkspaceClient

checks = [
    DQDatasetRule(
        check_func=check_funcs.foreign_key,
        check_func_kwargs={
            "columns": ["command_id"],
            "ref_columns": ["id"],
            "ref_table": "my_catalog.my_schema.command",
        },
    )
]
dq_engine = DQEngine(WorkspaceClient())
valid, invalid, observation = dq_engine.apply_checks_and_split(
    spark.read.table("my_catalog.my_schema.actions"), checks
)
```

Note: workspaces have no direct internet access — DQX wheels are downloaded locally
(`pip download --only-binary=:all: databricks-labs-dqx`), uploaded to a UC volume, and
installed with `pip install --no-index --find-links /Volumes/...`. See
`docs/guider/overvaake-og-drifte/bruke-dqx.md`.

When a check fails, always end with the triage question: should the expectation
change, should the data be cleaned, or should the source be contacted?

## Storage and performance

- **Clustering**: prefer Liquid Clustering (`CLUSTER BY AUTO`) — it can be changed
  later. Avoid partitioning unless you are certain (hard to reverse). Z-ordering must
  be re-specified on every `OPTIMIZE`.
- **Maintenance**: Predictive Optimization (automatic `OPTIMIZE`/`VACUUM`) is
  preferred; otherwise schedule them explicitly (VACUUM default retention 7 days).
- **Cluster sizing** (classic compute): table-to-table dataflow is worker-heavy and
  driver-light — a smaller driver instance saves money. Simple queries (no joins/aggs)
  → compute-optimized workers; complex → one large memory-heavy worker.
- Very high file counts → consider Auto Loader file-notification mode (requires
  platform-team infra change; not currently enabled).

## Spark code conventions

- Python 3.13+, modern type hints (`str | None`), Google-style docstrings, ruff.
- Business logic lives in `src/<package>/` as testable functions built into a wheel —
  notebooks orchestrate, they do not hold logic.
- Tests use pytest with a local Spark session from `conftest.py`; transformations
  should be pure `DataFrame -> DataFrame` functions so they run in tests without a
  workspace.
- Fully qualify tables as `${catalog}.${schema}.${table}` via bundle variables — never
  hardcode catalog names in code.
