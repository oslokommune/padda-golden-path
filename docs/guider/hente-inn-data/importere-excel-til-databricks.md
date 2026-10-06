---
title: Importere Excel til Databricks
description: Hvordan laste opp en Excel-fil til et volum og lage en tabell av den i Unity Catalog.
diataxis: how-to
---

# Importere Excel til Databricks

Denne guiden viser hvordan du får innholdet i en Excel-fil inn som en tabell i Unity
Catalog, rett fra nettleseren. Databricks leser `.xlsx` og `.xls` direkte.

## Før du begynner

Sørg for at du har:

- Teamets katalog. Vi bruker `min_katalog` som eksempel.
- Rett til å opprette volumer og tabeller i katalogen.
- En Excel-fil der første rad er kolonnenavn.

## Trinn 1: Opprett et volum

Åpne **Catalog** i sidemenyen, gå til skjemaet `landing_default` i katalogen din, og velg
**Create → Volume**. Gi volumet et navn, for eksempel `opplastinger`. Har teamet allerede
et volum for manuelle opplastinger, bruk det.

## Trinn 2: Last opp fila

Velg **Upload to this volume** på volumsiden, og last opp fila.

## Trinn 3: Lag tabellen

Åpne menyen ved fila i volumet og velg **Create table**. Velg ark og sett katalog, skjema
og tabellnavn, for eksempel `min_katalog`, `bronze_default` og `min_tabell`. Kontroller
forhåndsvisningen og trykk **Create table**.

## Bekreft resultatet

Åpne tabellen under **Catalog** i sidemenyen og kontroller at kolonnenavn og kolonnetyper
ble som forventet.

## Oppdatere tabellen når fila endres

Last opp den nye versjonen av fila til volumet, og gjør trinn 3 på nytt med **Overwrite
existing table** i stedet for **Create new table**.

!!! tip "Med SQL"
    Vil du heller skripte det, leser `read_files` fila fra SQL Editor eller en notebook:

    ```sql
    USE CATALOG min_katalog;

    CREATE OR REPLACE TABLE min_katalog.bronze_default.min_tabell AS
    SELECT *
    FROM read_files(
      '/Volumes/min_katalog/landing_default/opplastinger/min_fil.xlsx',
      format => 'excel',
      headerRows => 1,
      schemaEvolutionMode => 'none'
    );
    ```

    `USE CATALOG` må med, ellers feiler `CREATE OR REPLACE TABLE` med
    `UC_HIVE_METASTORE_DISABLED_EXCEPTION`. Uten `headerRows => 1` heter kolonnene `_c0`,
    `_c1` og så videre. Andre ark og celleområder velger du med `dataAddress`, se
    [Databricks-dokumentasjonen om Excel-filer](https://docs.databricks.com/aws/en/query/formats/excel).

## Feilsøking

??? failure "**Create table** er grået ut"

    Catalog Explorer mangler aktiv compute. Velg et aktivt warehouse eller serverless i
    compute-velgeren i Catalog Explorer, og prøv igjen.

??? failure "Du får feil om manglende rettigheter"

    Du mangler rettigheter i katalogen. Kontakt workspace-admin i teamet ditt, eller
    Dataspeilet i [#dig-dataspeilet-support](https://oslokommune.slack.com/archives/C01DE13PLDP).

??? failure "Tomme celler der arket har verdier"

    Sammenslåtte celler leses bare inn i cella øverst til venstre, resten blir `NULL`.
    Fjern sammenslåingene i Excel før du laster opp.

??? failure "Fila kan ikke leses"

    Passordbeskyttede filer og formatet Strict Open XML Spreadsheet støttes ikke. Lagre
    fila på nytt som vanlig `.xlsx` uten passord.

## Relatert innhold

- [Last opp ditt første datasett](../../kom-i-gang/last-opp-ditt-forste-datasett.md)
- [Datainnlasting](../../om-plattformen/konsepter/datainnlasting.md)
