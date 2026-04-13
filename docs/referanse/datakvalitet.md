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

DQX er et batteries-included rammeverk for datakvalitet. Det er ikke så mye man kan gjøre med DQX som man ikke kan gjøre med ren Databricks, men her slipper man å lage alt selv. Se [DQX how-to](../guider/overvaake-og-drifte/bruke-dqx.md) for mer informasjon om hvordan man bruker DQX.

## Relatert innhold

- [Avanserte expectations](https://docs.databricks.com/aws/en/ldp/expectation-patterns)
- [DQX how-to](../guider/overvaake-og-drifte/bruke-dqx.md)
