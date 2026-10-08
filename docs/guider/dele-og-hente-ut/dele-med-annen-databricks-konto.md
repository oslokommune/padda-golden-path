---
title: Dele data med en annen Databricks-konto
description: Hvordan dele tabeller fra katalogen din med et team som bruker Databricks i en annen konto, med OpenSharing og uten å kopiere dataene.
diataxis: how-to
---

# Dele data med en annen Databricks-konto

Denne guiden viser hvordan du deler tabeller fra katalogen din med et team som bruker
Databricks i en annen konto, for eksempel på Azure, med
[OpenSharing](https://docs.databricks.com/aws/en/opensharing). Mottakeren leser tabellene
direkte fra Padda, uten kopi, og ser alltid siste versjon.

Du trenger to objekter i Unity Catalog: en *mottaker* (recipient) for den andre
kontoen, som Dataspeilet oppretter, og en *share* med tabellene, som teamet oppretter og
gir mottakeren tilgang til. Eksempelet i denne guiden deler gold-tabellen
`gold_default.padder_per_dag` fra [Dokumentere et dataprodukt](dokumentere-dataprodukt.md)
med en fiktiv mottaker, Padderegisteret. Bytt ut navnene med dine egne.

Deling med et annet team innad på Padda går ikke via OpenSharing, se [Eierskap og
forvaltning](../../om-plattformen/konsepter/eierskap-og-forvaltning.md#tilgangsbeslutninger).

## Før du begynner

Sørg for at du har:

- Avklart med dataprodukteieren at dataene kan deles med mottakeren, og dokumentert
  bruksretten, se [Eierskap og
  forvaltning](../../om-plattformen/konsepter/eierskap-og-forvaltning.md#tilgangsbeslutninger).
- Tabellene i prod-katalogen, dokumentert slik at mottakeren forstår dem, se [Dokumentere
  et dataprodukt](dokumentere-dataprodukt.md).
- En kontaktperson hos mottakeren som kan hente sharing ID-en deres og opprette katalogen
  hos dem.
- En workspace-admin på teamet til trinn 2 og 3, enten deg selv eller noen som kan gjøre
  det for deg, se [Roller og
  rettigheter](../../referanse/roller-og-rettigheter.md#workspace-admin).

SQL-en i guiden kjører du i SQL-editoren i prod-workspacet.

## Trinn 1: Bestill mottaker hos Dataspeilet

Mottakeren identifiseres med sharing ID-en til den andre kontoen. Be kontaktpersonen hos
mottakeren hente den ved å kjøre dette i workspacet de skal lese dataene fra:

```sql
SELECT CURRENT_METASTORE();
```

ID-en har formen `azure:westeurope:5683e486-66c7-7efc-ed52-ae3a12de1a23`. Den gir ingen
tilgang i seg selv, så den kan sendes i klartekst.

Send så en melding i
[#dig-dataspeilet-support](https://oslokommune.slack.com/archives/C01DE13PLDP) med sharing
ID-en, navnet på organisasjonen og kontaktpersonen hos mottakeren, og hvilket team som
bestiller. Dataspeilet oppretter mottakeren og svarer med navnet på den, på formen
`<mottaker>_<miljø>`, se
[Navnekonvensjoner](../../referanse/navnekonvensjoner.md#shares-og-mottakere). Guiden
bruker navnet `padderegisteret_prod`. Deler et annet team på Padda allerede med samme
konto, finnes mottakeren fra før, og du får navnet på den. Er det første gang teamet ditt
deler, setter Dataspeilet samtidig opp rettighetene teamet trenger for å dele.

## Trinn 2: Opprett sharen og legg til tabellene

Opprett en share med navn på formen `<org>_<dataprodukt>`, og legg til tabellene som skal
deles:

```sql
CREATE SHARE dig_eksempel_paddeobservasjoner
  COMMENT 'Paddeobservasjoner per dag fra Oslo kommune. Kontakt: #padda-padder på Slack.';

ALTER SHARE dig_eksempel_paddeobservasjoner
  ADD MATERIALIZED VIEW dig_eksempel_prod_green.gold_default.padder_per_dag;
```

Gold-tabeller fra en Declarative Pipeline er materialized views. Bruk `ADD TABLE` for
vanlige tabeller og streaming tables, og `ADD VIEW` for views. Vil du dele et helt skjema,
også tabeller som kommer til senere, bruker du `ADD SCHEMA`.

## Trinn 3: Gi mottakeren tilgang

```sql
GRANT SELECT ON SHARE dig_eksempel_paddeobservasjoner TO RECIPIENT padderegisteret_prod;
```

`SELECT` er den eneste rettigheten en mottaker kan få på en share. Gi beskjed til
kontaktpersonen hos mottakeren om at sharen er klar. Hos dem vises den under leverandøren
`dig_oslo_kommune`.

## Bekreft resultatet

Kontroller at sharen inneholder tabellen, og at mottakeren har fått den:

```sql
SHOW ALL IN SHARE dig_eksempel_paddeobservasjoner;
SHOW GRANTS TO RECIPIENT padderegisteret_prod;
```

Den første lister objektene i sharen, den andre skal vise sharen med rettigheten
`SELECT`. Når mottakeren har opprettet en katalog for sharen, se under, skal de kunne lese
tabellen.

## Hos mottakeren

Mottakeren gjør sharen tilgjengelig ved å opprette en katalog for den. Det krever
rettighetene `CREATE CATALOG` og `USE PROVIDER` i Unity Catalog hos mottakeren. Send
gjerne dette til kontaktpersonen:

```sql
CREATE CATALOG padda_paddeobservasjoner
  USING SHARE dig_oslo_kommune.dig_eksempel_paddeobservasjoner;

SELECT * FROM padda_paddeobservasjoner.gold_default.padder_per_dag LIMIT 10;
```

Katalogen er skrivebeskyttet, og mottakeren styrer selv hvem hos dem som får lese den,
med vanlige grants. Delte views og materialized views leses best fra et SQL Warehouse
eller serverless compute.

## Endre eller stoppe delingen

Legg til og fjern objekter med `ALTER SHARE … ADD` og `ALTER SHARE … REMOVE`. Trekk
tilbake tilgangen med `REVOKE SELECT ON SHARE … FROM RECIPIENT …`, og slett sharen med
`DROP SHARE` når delingen er over. Mottakeren forvaltes av Dataspeilet og blir stående,
siden andre team kan dele med samme konto.

## Feilsøking

??? failure "Du får ikke lov til å opprette sharen eller gi tilgang"

    Rettighetene til å dele ligger på workspace-admin-gruppa og gis av Dataspeilet ved
    første bestilling. Sjekk at du er medlem av gruppa, og at bestillingen er ferdig
    behandlet.

??? failure "Mottakeren ser ikke sharen"

    - Har mottakeren workspaces i flere regioner eller kontoer, har de flere sharing ID-er.
      ID-en må komme fra workspacet de skal lese fra.
    - Kontaktpersonen må ha `CREATE CATALOG` og `USE PROVIDER` i Unity Catalog hos
      mottakeren for å se leverandører og opprette katalogen.

??? failure "Tabellen kan ikke legges til i sharen"

    Tabeller med radfiltre eller kolonnemasker kan ikke deles. Lag et view med bare de
    radene og kolonnene mottakeren skal se, og del viewet med `ADD VIEW`.

## Relatert innhold

**Guider:**

- [Dokumentere et dataprodukt](dokumentere-dataprodukt.md)

**Forklaringer:**

- [Eierskap og forvaltning](../../om-plattformen/konsepter/eierskap-og-forvaltning.md)
- [Klassifisering av sensitivitet](../../om-plattformen/konsepter/klassifisering-sensitivitet.md)

**Referanser:**

- [Navnekonvensjoner](../../referanse/navnekonvensjoner.md)
- [Roller og rettigheter](../../referanse/roller-og-rettigheter.md)
- [Definisjon av dataprodukt](../../referanse/dataprodukt.md)

**Ekstern dokumentasjon:**

- [What is OpenSharing?](https://docs.databricks.com/aws/en/opensharing)
- [What is the OpenSharing Databricks-to-Databricks protocol?](https://docs.databricks.com/aws/en/opensharing/share-data-databricks)
- [Create shares for OpenSharing](https://docs.databricks.com/aws/en/opensharing/create-share)
- [Read data shared using Databricks-to-Databricks OpenSharing (for recipients)](https://docs.databricks.com/aws/en/opensharing/read-data-databricks)
- [Audit and monitor data sharing](https://docs.databricks.com/aws/en/opensharing/audit-logs)
