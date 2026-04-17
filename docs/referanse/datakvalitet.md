---
title: Datakvalitet
description: Referanse for mekanismer og verktøy for datakvalitet på Databricks-plattformen.
diataxis: reference
---

# Datakvalitet

Mekanismer og verktøy for å validere og overvåke datakvalitet på Databricks-plattformen. Dekker innebygde Databricks-funksjoner (Constraints, Expectations, Alerts) og det eksterne Python-rammeverket DQX.

## Oversikt

- **Type:** Verktøy og mekanismer
- **Gjelder for:** Databricks-plattformen
- **Komponenter:** Constraints (Delta-tabeller), Expectations (Declarative Pipelines), Alerts, DQX
- **Avhengigheter:** DQX krever manuell installasjon i lukket nettverksmiljø

## Innebygde mekanismer i Databricks

Databricks tilbyr en [oversikt](https://www.databricks.com/discover/pages/data-quality-management) over innebygde verktøy for datakvalitet.

### Constraints og Expectations

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

Her er `NOT NULL` og `dateWithinRange` constraints. Disse håndheves strengt, og et forsøk på å sette inn rader som ikke oppfyller kravene vil feile. `PRIMARY KEY` og `FOREIGN KEY` er strengt tatt også constraints, men håndheves ikke. De har andre funksjoner.

Declarative Pipelines har `NOT NULL` på lik linje med normale delta-tabeller, men `CONSTRAINT`-ordet fungerer litt annerledes. `CHECK` støttes ikke, men i stedet brukes `EXPECT`. Her er `valid_customer_age` ikke en constraint men en [expectation](https://docs.databricks.com/aws/en/ldp/expectations):

```sql
CREATE OR REFRESH STREAMING TABLE customers(
  CONSTRAINT valid_customer_age EXPECT (age BETWEEN 0 AND 120)
) AS SELECT * FROM STREAM(datasets.samples.raw_customers);
```

Den største forskjellen mellom constraints og expectations er at expectations kan håndheves på tre måter: WARN, DROP ROW, og FAIL. _WARN er default_.

De tre håndhevingsmodiene for expectations:

| Modus            | Oppførsel                                |
| ---------------- | ---------------------------------------- |
| `WARN` (default) | Logger avvik, setter inn alle rader      |
| `DROP ROW`       | Forkaster rader som bryter forventningen |
| `FAIL UPDATE`    | Stopper hele pipeline-kjøringen          |

### Alerts

[Alerts](https://docs.databricks.com/aws/en/sql/user/alerts/) er SQL-spørringer som kjører på definerte intervaller. Et alert utløses når spørringsresultatet avviker fra en definert betingelse, og sender varsel per e-post til konfigurerte mottakere.

## Verktøy i DQX

DQX er et Python-rammeverk for datakvalitet med et sett av ferdiglagde sjekkfunksjoner og regelobjekter. Det er installert som et eksternt bibliotek og krever manuell oppsett i lukkede nettverksmiljøer.

### Funksjoner

`databricks.labs.dqx.check_funcs` inneholder alle innebygde sjekkfunksjoner. Eksempler på funksjoner som ikke har direkte ekvivalent i Constraints eller Expectations:

- `is_unique` — validerer at en kolonne eller sammensatt nøkkel er unik
- `is_aggr_equal` — validerer at et aggregat er lik en forventet verdi
- `is_data_fresh` — validerer at data ikke er eldre enn en gitt tidsgrense

### Regler

Sjekkfunksjonene brukes som argumenter til regelobjekter i `databricks.labs.dqx.rule`:

```python
DQDatasetRule(  # check uniqueness of composite key
    criticality="error", check_func=check_funcs.is_unique, columns=["col1", "col2"]
)
```

Se offisiell dokumentasjon for [flere eksempler](https://databrickslabs.github.io/dqx/docs/guide/quality_checks_definition/).

## Begrensninger

- `PRIMARY KEY` og `FOREIGN KEY` håndheves ikke.
- Expectations med `WARN` (default) logger avvik uten å påvirke datainnsetting.
- DQX krever manuell installasjon i lukkede nettverksmiljøer uten internettilgang.

## Relatert innhold

**Guider:**

- [DQX installasjon og bruk](../guider/overvaake-og-drifte/bruke-dqx.md)

**Forklaringer:**

- [Hva er datakvalitet](../om-plattformen/konsepter/datakvalitet.md)

**Ekstern dokumentasjon:**

- [Avanserte expectations](https://docs.databricks.com/aws/en/ldp/expectation-patterns)
- [DQX brukermanual](https://databrickslabs.github.io/dqx/docs/guide/)
- [DQX funksjoner](https://github.com/databrickslabs/dqx/blob/main/src/databricks/labs/dqx/check_funcs.py)
- [Bundle med bruk av DQX og alert](https://github.com/oslokommune/padda-databrikker/tree/main/bundles/datakvalitet_dqx)
