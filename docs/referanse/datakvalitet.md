---
title: Datakvalitet
description: Verktøy for datakvalitet.
diataxis: reference
---

# Datakvalitet

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

## Verktøy i DQX

DQX er et batteries-included Python-rammeverk for datakvalitet. Det er ikke så mye man kan gjøre med DQX som man ikke kan gjøre med ren Databricks, men her slipper man å lage alt selv. Bruk av biblioteker og rammeverk i et system uten internett kan være litt vanskelig. Se [DQX how-to](../guider/overvaake-og-drifte/bruke-dqx.md) for en guide til hvordan man installerer og bruker DQX uten internett.

### Funksjoner

`databricks.labs.dqx.check_funcs` er modulen der alle sjekkene ligger. Eksempler på funksjoner man ikke får til med kun constraints/expectations er `is_unique`, `is_aggr_equal` og `is_data_fresh`. Man kan få til lignende med alerts i Databricks, men her er det altså litt ferdiglagd.

### Regler

Funksjonene kan ikke brukes alene, men brukes som argumenter til regler. De forskjellige reglene ligger i `databricks.labs.dqx.rule`. Eksempel:

```python
DQDatasetRule(  # check uniqueness of composite key
  criticality="error",
  check_func=check_funcs.is_unique,
  columns=["col1", "col2"]
)
```

Se offisiell dokumentasjon for [flere eksempler](https://databrickslabs.github.io/dqx/docs/guide/quality_checks_definition/).

## Relatert innhold

- [Avanserte expectations](https://docs.databricks.com/aws/en/ldp/expectation-patterns)
- [DQX installasjon](../guider/overvaake-og-drifte/bruke-dqx.md)
- [DQX brukermanual](https://databrickslabs.github.io/dqx/docs/guide/)
- [DQX funksjoner](https://github.com/databrickslabs/dqx/blob/main/src/databricks/labs/dqx/check_funcs.py)
- [Hva er datakvalitet](../om-plattformen/konsepter/datakvalitet.md)
