---
title: Lagring og ytelse
description: Oversikt over strategier for datagruppering og vedlikeholdsoperasjoner for Delta-tabeller i Databricks.
diataxis: reference
---

# Lagring og ytelse

Oversikt over tilgjengelige strategier for å kontrollere fysisk gruppering av data på disk, samt vedlikeholdsoperasjoner for Delta-tabeller i Databricks.

## Oversikt

- **Type:** Konfigurasjon og vedlikehold
- **Gjelder for:** Delta-tabeller i Databricks (Delta Lake)
- **Standardoppførsel:** Ingen eksplisitt datagruppering; filer skrives i ankomstrekkefølge
- **Avhengigheter:** Databricks Runtime, Delta Lake

## Grupperingsstrategier

Tre strategier er tilgjengelige for å kontrollere hvordan data grupperes fysisk i Parquet-filer på disk.

| Strategi                                                                 | Beskrivelse                                                                                                                                                 | Passer for                                                                                                                                                                         |
| ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Liquid Clustering](https://docs.databricks.com/aws/en/delta/clustering) | Databricks-administrert strategi som automatisk omorganiserer data basert på angitte kolonner. Kan endres uten å skrive om tabellen.                        | Tabeller med varierende eller uforutsigbare spørringsmønstre.                                                                                                                      |
| [Partisjonering](https://docs.databricks.com/aws/en/tables/partitions)   | Data deles inn i fysisk separate kataloger basert på distinkte verdier i én kolonne. Vanskelig å endre på. Se advarsel.                                     | Tabeller med én kolonne med et begrenset antall distinkte verdier (i hundrevis) som konsekvent brukes i WHERE-setninger. Eksempel på egnede kolonner: Dato eller transaksjonstype. |
| [Z-ordering](https://docs.databricks.com/aws/en/delta/data-skipping)     | Co-lokaliserer relaterte data i de samme Parquet-filene slik at Databricks kan hoppe over irrelevante filer under spørringer basert på min/maks-statistikk. | Tabeller med høy lesefrekvens der spørringer filtrerer på bestemte kolonner. Eksempel på egnet kolonne: Bruker-ID.                                                                 |

## Vedlikeholdsoperasjoner

To tilnærminger finnes for å kjøre `OPTIMIZE` og `VACUUM` på Delta-tabeller.

### Prediktiv optimalisering

En Databricks-funksjon som automatisk utløser `OPTIMIZE` og `VACUUM` basert på observerte bruksmønstre. Krever ingen eksplisitt planlegging eller manuell kjøring. Praktisk erfaring med dette har vært litt blandet.

### Eksplisitt OPTIMIZE og VACUUM

Manuelt planlagte vedlikeholdsoperasjoner:

- **`OPTIMIZE`** komprimerer små Parquet-filer til større filer for å redusere fragmentering og forbedre spørringsytelse.
- **`VACUUM`** sletter Parquet-filer som ikke lenger er referert til av Delta-loggen, og frigjør lagringsplass. Standard oppbevaringsperiode er 7 dager.

## Begrensninger

- Partisjonering på kolonner med svært høy kardinalitet (mange distinkte verdier) kan gi dårligere ytelse enn ingen partisjonering.
- Z-ordering må angis eksplisitt ved hver `OPTIMIZE`-kjøring for å opprettholdes.
- Liquid Clustering krever Databricks Runtime 13.3 eller nyere.

!!! warning "Partisjonering er vanskelig å reversere"
En partisjonert tabell kan ikke enkelt ompartisjoneres eller avpartisjoneres — det krever
full omskriving av tabellen. Valget bør gjøres med omhu før tabellen tas i produksjon.

## Relatert innhold

- [Databricks om underliggende data layout](https://www.databricks.com/discover/pages/optimize-data-workloads-guide#data-layout)
