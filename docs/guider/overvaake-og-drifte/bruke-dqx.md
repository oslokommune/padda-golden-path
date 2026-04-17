---
title: Installere og bruke DQX
description: Hvordan installere DQX i et Databricks-miljø uten internettilgang og kjøre datakvalitetskontroller mot Unity Catalog-tabeller.
diataxis: how-to
---

# Installere og bruke DQX

Denne veiledningen viser deg hvordan du installerer DQX i et Databricks-miljø uten direkte internettilgang og kjører datakvalitetskontroller mot tabeller i Unity Catalog.

## Før du begynner

Sørg for at du har:

- Pip installert lokalt
- Tilgang til et Databricks-arbeidsområde
- Et Unity Catalog-volum du kan laste opp filer til
- Tilgang til tabellene du vil kjøre kontroller mot

## Trinn 1: Last ned DQX og avhengigheter lokalt

Kjør følgende kommando lokalt for å laste ned DQX og alle avhengigheter som `.whl`-filer:

```sh
pip download --python-version=3.12 --only-binary=:all: databricks-labs-dqx
```

Python-versjonen må matche den som brukes i omgivelsen notebooken kjøres i.

Filene lagres i gjeldende mappe.

## Trinn 2: Last opp pakkene til et Databricks-volum

Last opp alle nedlastede `.whl`-filer til et Unity Catalog-volum. Du kan gjøre dette via Databricks UI under **Catalog → Volumes**, eller med Databricks CLI:

```sh
databricks fs cp *.whl dbfs:/Volumes/min_katalog/mitt_skjema/mitt_volum/
```

## Trinn 3: Installer DQX i notebooken

Legg til følgende som første celle i notebooken din:

```sh
%sh
pip install --no-index --find-links /Volumes/min_katalog/mitt_skjema/mitt_volum databricks_labs_dqx
```

## Trinn 4: Kjør datakvalitetskontroller

Definer kontrollene og kjør dem mot tabellen din. Eksempelet nedenfor sjekker at foreign key-relasjonen mellom `actions.command_id` og `command.id` holder:

```python
from databricks.labs.dqx.engine import DQEngine
from databricks.labs.dqx import check_funcs
from databricks.labs.dqx.rule import DQDatasetRule
from databricks.labs.dqx.contexts.workspace_context import WorkspaceContext
from databricks.labs.dqx.metrics_observer import DQMetricsObserver
from databricks.sdk import WorkspaceClient

all_checks = [
    DQDatasetRule(
        check_func=check_funcs.foreign_key,
        check_func_kwargs={
            "columns": ["command_id"],
            "ref_columns": ["id"],
            "ref_table": "padda_dev_green.silver_default.command",
        },
    )
]

observer = DQMetricsObserver(name="dq_metrics")
dq_engine = DQEngine(WorkspaceClient(), observer=observer)

input_df = spark.read.table("padda_dev_green.silver_default.actions")
valid, invalid, observation = dq_engine.apply_checks_and_split(input_df, all_checks)

display(invalid)
```

## Bekreft resultatet

Sjekk `invalid`-dataframen etter at cellen er ferdig kjørt:

- **Tom DataFrame** — alle rader bestod kontrollene.
- **Rader i DataFrame** — disse radene brøt minst én kontroll. Kolonnene `_errors` og `_warnings` beskriver hvilken sjekk som feilet og hvorfor.

For å se en oppsummering av observerte metrikker:

```python
invalid.count()
valid.count()
display(observation.get)
```

## Relatert innhold

- [DQX brukermanual](https://databrickslabs.github.io/dqx/docs/guide/)
- [Datakvalitet](../../referanse/datakvalitet.md)
- [Bundle med bruk av DQX](https://github.com/oslokommune/padda-databrikker/tree/main/bundles/datakvalitet_dqx)
