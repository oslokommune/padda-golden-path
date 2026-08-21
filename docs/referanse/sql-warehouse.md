---
title: SQL Warehouse
description: Tilgjengelige SQL Warehouses, konfigurasjon, tilkoblingsdetaljer, tilganger og begrensninger.
diataxis: reference
---

# SQL Warehouse

Et SQL Warehouse er Databricks sin compute for SQL-spørringer. Det brukes av SQL-editoren
og dashbord i Databricks, av BI-verktøy som Power BI, og av jobber som oppdaterer Power
BI-modeller. Hvert workspace har tre ferdig oppsatte warehouses som Dataspeilet forvalter.

## Tilgjengelige warehouses

Alle workspaces har de samme tre warehousene:

| Navn       | Databricks-størrelse | Stopper automatisk etter |
|------------|----------------------|--------------------------|
| **Small**  | 2X-Small             | 20 minutter              |
| **Medium** | X-Small              | 15 minutter              |
| **Large**  | Small                | 10 minutter              |

Alle tre er av typen **PRO**, som blant annet kreves for å kjøre notebooks mot et
warehouse.

## Oppstart og stopp

Et stoppet warehouse starter automatisk når noen kjører en spørring mot det, kobler til
via JDBC/ODBC, åpner et dashbord som bruker det, eller når en jobb trenger det.
Oppstarten tar typisk noen minutter, så jobber og rapporter som treffer et stoppet
warehouse må regne med denne ventetiden.

Et warehouse uten aktivitet stopper av seg selv etter tiden angitt i tabellen over, slik
at det bare koster penger mens det kjører.

## Tilkoblingsdetaljer

Tilkoblingsdetaljene for et warehouse ligger i Databricks-workspacet under **SQL
Warehouses** → `<navn på warehouset>` → **Connection details**:

| Felt                                 | Brukes av                                           |
|--------------------------------------|-----------------------------------------------------|
| **Server hostname** og **HTTP path** | Klienter som kobler til via JDBC/ODBC, som Power BI |
| Warehouse-ID                         | Bundles og API-er                                   |

Warehouse-ID-en vises ikke som et eget felt, men er siste ledd i **HTTP path**
(`/sql/1.0/warehouses/<warehouse-id>`).

Pålogging skjer med kommunebrukeren din — se [Hvordan koble Power BI til
Databricks](../guider/dele-og-hente-ut/koble-til-power-bi.md) for hvordan det gjøres i
praksis.

## Tilganger

Alle brukere i et workspace kan bruke og starte warehousene (rettigheten `CAN_USE` i
Databricks). Konfigurasjonen — størrelser, automatisk stopp og rettigheter — forvaltes av
Dataspeilet og kan ikke endres av teamene selv.

## Begrensninger

- **Kun SQL.** Notebooks som kjører mot et SQL Warehouse kan bare kjøre SQL-celler.
  Python og andre språk krever et cluster eller serverless compute.

- **Ingen utskalering.** Hvert warehouse består av ett enkelt cluster og skalerer ikke ut
  ved samtidig bruk. Spørringer utover kapasiteten legges i kø til warehouset får ledig
  kapasitet.

## Overvåking

Fanen **Monitoring** på hvert warehouse viser kjørende spørringer, spørringer i kø og
antall aktive clustere. Spørringshistorikken i workspacet viser tidligere spørringer med
status, kjøretid og en spørringsprofil for feilsøking av trege spørringer.

## Relatert innhold

- [Hvordan koble Power BI til Databricks](../guider/dele-og-hente-ut/koble-til-power-bi.md)
  — koble Power BI Desktop til et warehouse og bygg rapporter
- [Hvordan oppdatere Power BI-modeller automatisk](../guider/dele-og-hente-ut/oppdatere-power-bi-modeller-automatisk.md)
  — la en jobb oppdatere semantiske modeller via warehouset
- [Databricks sin dokumentasjon om SQL warehouses](https://docs.databricks.com/aws/en/compute/sql-warehouse/)
