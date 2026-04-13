---
title: Datakvalitet
description: Hva er datakvalitet og hvordan sikre det.
diataxis: reference
---

# Datakvalitet

Kvaliteten på data er en måte å snakke om hvor formålstjenlig dataen er. Dette inkluderer ikke bare hvor godt dataen speiler virkeligheten, men også hvor ryddig den er. Bruk av forskjellige synonymer i tekstfelt og dupliserte rader er eksempler på data som ikke strengt tatt er uriktig, men som gjerne resulterer i feil resultat når dataen blir analysert. For at data skal ha høy kvalitet må det altså gi en analytiker et riktig bilde av virkeligheten, og da må dataen ikke bare ikke være uriktig men heller ikke være misvisende. [Det finnes forskjellige definisjoner](https://en.wikipedia.org/wiki/Data_quality#Dimensions_of_data_quality) av hva datakvalitet er, men [Databricks definerer det slik](https://www.databricks.com/blog/what-is-data-quality):

- Dataen skal være konsekvent med andre datasett
- Hver rad skal være nøyaktig og feilfri
- Dataen skal være i riktig og forventet format
- Dataen skal være fullstendig
- Dataen skal være oppdatert
- Det skal ikke forekomme duplikater

## Innebygde mekanismer i Databricks

Databricks har selv en oversikt [her](https://www.databricks.com/discover/pages/data-quality-management) over de verktøyene de tilbyr for å trygge kvaliteten på data.

### Expectations og Constraints

Databricks har to relaterte mekanismer for å sjekke at rader er gyldige. Expectations er for Declarative Pipelines, og Constraints er for normale delta-tabeller.

[Constraints](https://docs.databricks.com/aws/en/tables/constraints) ser sånn ut:

```sql
CREATE TABLE people10m (
  id INT NOT NULL PRIMARY KEY,
  firstName STRING NOT NULL,
  middleName STRING,
  lastName STRING,
  gender STRING,
  birthDate TIMESTAMP,
  ssn STRING,
  salary INT,
  CONSTRAINT dateWithinRange CHECK (birthDate > '1900-01-01')
);
```

Her er `NOT NULL` og `dateWithinRange` constraints. Disse håndheves strengt, og et forsøk på å sette inn rader som ikke oppfyller kravene vil feile. `PRIMARY KEY` er strengt tatt også en constraint, men denne håndheves ikke i det hele tatt, og er nesten kun dokumentasjon.

Declarative Pipelines har `NOT NULL` på lik linje med normale delta-tabeller, men `CONSTRAINT`-ordet fungerer litt annerledes. `CHECK` støttes ikke, men i stedet brukes `EXPECT`. Her er `valid_customer_age` ikke en constraint men en [expectation](https://docs.databricks.com/aws/en/ldp/expectations):

```sql
CREATE OR REFRESH STREAMING TABLE customers(
  CONSTRAINT valid_customer_age EXPECT (age BETWEEN 0 AND 120)
) AS SELECT * FROM STREAM(datasets.samples.raw_customers);
```

Den største forskjellen mellom constraints og expectations er at expectations kan håndheves på tre måter: WARN, DROP ROW, og FAIL. _WARN er default_ og gjør ingenting annet enn å logge, så vær obs!

### Alerts

[Alerts](https://docs.databricks.com/aws/en/sql/user/alerts/) lar deg definere SQL-spørringer som kjører ved gitte mellomrom, definere hvordan resultatet skal se ut, og hvem som skal få epost når dette ikke stemmer.

## DQX

DQX er et batteries-included rammeverk for datakvalitet. Det er ikke så mye man kan gjøre med DQX som man ikke kan gjøre med ren Databricks, men her slipper man å lage alt selv.

### Installering

Først må du lokalt kjøre noe slikt som `pip download --python-version=3.12 --only-binary=:all: databricks-labs-dqx`. Dette laster ned alle avhengigheter lokalt. Deretter kan du finne et passende volum å last disse opp til. Når det er gjort, kan du lage en notebook med dette som første celle:

```sh
%sh
pip install --no-index --find-links /Volumes/min_katalog/mitt_skjema/mitt_volum databricks_labs_dqx
```

Deretter kan DQX brukes i de følgende cellene i notebooken.

### Eksempel

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

- DQX [brukermanual](https://databrickslabs.github.io/dqx/docs/guide/)
- DQX [funksjoner](https://github.com/databrickslabs/dqx/blob/main/src/databricks/labs/dqx/check_funcs.py)
- [Avanserte expectations](https://docs.databricks.com/aws/en/ldp/expectation-patterns)
