Team dataspeilet vedlikeholder Brolagt sti for en rekke use cases.


Repoer og hva de inneholder / monorepo for alt utenom IaC.


For en oversikt av use cases som er støttet gjennom Brolagt sti, se repo:

```javascript
git clone padda-golden-path
```

Det er satt opp et bibliotek for generelle pipelines:


```javascript
git clone padda-pipeline-lib
```

Hver domene (område) har et eget Github repo


```bash
domene-bundle/                            # domene repo eksempel
├─ bundles/
│  ├─ dataprodukt/                        # <- en deploy-bar bundle
│  │  ├─ databricks.yml
│  │  ├─ resources/
│  │  │  ├─ dataprodukt.pipeline.yml      # Lakeflow pipeline
│  │  │  ├─ dataprodukt_refresh.job.yml   # job som refresher dataset
│  │  │  └─ quality_monitor.yml           # data quality monitor
│  │  ├─ src/
│  │  │  ├─ notebooks/
│  │  │  └─ python/
│  │  └─ tests/
│  │     ├─ unit/
│  │     └─ integration/
│  └─ dataprodukt-2/
│     └─ ... (samme struktur som over)
├─ shared/                                # domene-shared
│  ├─ variables.yml                       # domene defaults
│  └─ libs/
│     └─ domene_utils.py
└─ .github/workflows/
├─ pr-dev.yml                          # per-PR deploy til dev
└─ main-prod.yml
```


devx:

lint

pre-commit hooks
