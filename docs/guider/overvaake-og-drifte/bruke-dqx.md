---
title: Installere og bruke DQX
description: Hvordan bruke DQX til å sikre datakvalitet.
diataxis: how-to
---

# Installere og bruke DQX

DQX er et batteries-included rammeverk for datakvalitet. Det er ikke så mye man kan gjøre med DQX som man ikke kan gjøre med ren Databricks, men her slipper man å lage alt selv.

## Installering

Først må du lokalt kjøre noe slikt som `pip download --python-version=3.12 --only-binary=:all: databricks-labs-dqx`. Dette laster ned alle avhengigheter lokalt. Deretter kan du finne et passende volum å last disse opp til. Når det er gjort, kan du lage en notebook med dette som første celle:

```sh
%sh
pip install --no-index --find-links /Volumes/min_katalog/mitt_skjema/mitt_volum databricks_labs_dqx
```

Deretter kan DQX brukes i de følgende cellene i notebooken.

## Eksempel

Denne notebooken sjekker at verdiene i `actions.comand_id` er et subset av `command.id`, slik at foreign key-relasjonen mellom de to kolonnene holder.

```python
# Databricks notebook source
# MAGIC %sh
# MAGIC pip install --no-index --find-links /Volumes/min_katalog/mitt_skjema/mitt_volum databricks_labs_dqx

# COMMAND ----------

from databricks.labs.dqx.engine import DQEngine
from databricks.labs.dqx import check_funcs
from databricks.labs.dqx.rule import DQRowRule, DQDatasetRule, DQForEachColRule

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

from databricks.labs.dqx.contexts.workspace_context import WorkspaceContext
from databricks.labs.dqx.metrics_observer import DQMetricsObserver

# Create an observer for general metrics collection
observer = DQMetricsObserver(name="dq_metrics")
# Create DQEngine instance to run checks
dq_engine = DQEngine(WorkspaceClient(), observer=observer)
input_df = spark.read.table("padda_dev_green.silver_default.actions")
# input_df - is a dataframe to validate; all_checks - is a list of checks to apply
valid, invalid, observation = dq_engine.apply_checks_and_split(input_df, all_checks)

display(invalid)
```

## Relatert innhold

- [DQX brukermanual](https://databrickslabs.github.io/dqx/docs/guide/)
- [Datakvalitet](../../referanse/datakvalitet.md)
