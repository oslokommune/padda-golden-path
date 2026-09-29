---
title: Dokumentere et dataprodukt
description: Hvordan beskrive en gold-tabell i pipeline-koden slik at konsumenter finner, forstår og kan bruke den uten å spørre teamet.
diataxis: how-to
---

# Dokumentere et dataprodukt

Et [dataprodukt](../../om-plattformen/konsepter/dataprodukter.md) skal være dokumentert
slik at konsumenter forstår innholdet uten å spørre noen. På plattformen bor
dokumentasjonen i Unity Catalog. Denne guiden viser hvordan du skriver tabellbeskrivelse,
kolonnebeskrivelser og angir primærnøkkel i pipeline-koden, så dokumentasjonen deployes,
versjoneres og gjennomgås sammen med tabellen den beskriver. Eksemplet bygger videre på
gold-tabellen `gold_default.padder_per_dag` fra [Skrive
transformasjoner](../bearbeide-data/skrive-transformasjoner.md). Bytt ut navn og tekster
med dine egne.

## Før du begynner

Sørg for at du har:

- En gold-tabell definert i en Declarative Pipeline i bundlen din, se [Skrive
  transformasjoner](../bearbeide-data/skrive-transformasjoner.md). Guiden bruker fila
  `src/paddeobservasjoner/transformations/gold_padder_per_dag.sql` eller `.py`,
  ressursnøkkelen `paddeobservasjoner_pipeline` og target `stage`.
- Avklart hvem som svarer for dataproduktet, og hvilken kanal konsumenter skal bruke for
  spørsmål, se [Eierskap og
  forvaltning](../../om-plattformen/konsepter/eierskap-og-forvaltning.md).
- Databricks CLI innlogget mot stage-workspacet, se [Sett opp
  utviklingsmiljøet](../../kom-i-gang/dev-setup.md).

## Trinn 1: Skriv tabellbeskrivelsen

Tabellbeskrivelsen er det første en konsument leser. Skriv den for noen som ikke kjenner
pipelinen, og få med:

- hva én rad er
- hva tabellen er laget for, og eventuelt hva den ikke egner seg til
- hvor dataene kommer fra, og hvor ofte de oppdateres
- kjente begrensninger
- hvor konsumenter kan stille spørsmål

Beskrivelsen kan bruke Markdown, som Catalog Explorer viser formatert.

!!! note "Hvorfor kontaktpunktet må stå i beskrivelsen"

    Eieren Catalog Explorer viser, er bare identiteten pipelinen kjører som, i produksjon
    en service principal. Den sier ingenting om hvem konsumenter kan spørre.

Legg beskrivelsen i `COMMENT` på tabellen:

=== "SQL"

    I fila `src/paddeobservasjoner/transformations/gold_padder_per_dag.sql`:

    ```sql
    CREATE OR REFRESH MATERIALIZED VIEW gold_default.padder_per_dag
      COMMENT 'Antall paddeobservasjoner og antall padder per dag, summert over alle lokaliteter. Én rad per dag med minst én observasjon.

    **Formål:** følge utviklingen i paddebestanden gjennom sesongen. Egner seg ikke til å sammenligne lokaliteter, siden alle er slått sammen.

    **Kilde:** feltregistreringer i `silver_default.paddeobservasjoner`. Oppdateres daglig etter innlasting.

    **Begrensninger:** antallet er observatørens telling, ikke et bestandsestimat.

    **Kontakt:** #padda-padder på Slack.'
      AS
    SELECT
      DATE(observert) AS dato,
      COUNT(*) AS antall_observasjoner,
      SUM(antall) AS antall_padder
    FROM
      silver_default.paddeobservasjoner
    GROUP BY
      DATE(observert);
    ```

=== "Python"

    I fila `src/paddeobservasjoner/transformations/gold_padder_per_dag.py`:

    ```python
    from pyspark import pipelines as dp
    from pyspark.sql import functions as F

    BESKRIVELSE = """Antall paddeobservasjoner og antall padder per dag, summert over alle lokaliteter. Én rad per dag med minst én observasjon.

    **Formål:** følge utviklingen i paddebestanden gjennom sesongen. Egner seg ikke til å sammenligne lokaliteter, siden alle er slått sammen.

    **Kilde:** feltregistreringer i `silver_default.paddeobservasjoner`. Oppdateres daglig etter innlasting.

    **Begrensninger:** antallet er observatørens telling, ikke et bestandsestimat.

    **Kontakt:** #padda-padder på Slack."""


    @dp.materialized_view(
        name="gold_default.padder_per_dag",
        comment=BESKRIVELSE,
    )
    def padder_per_dag():
        return (
            spark.read
            .table("silver_default.paddeobservasjoner")
            .groupBy(F.to_date("observert").alias("dato"))
            .agg(
                F.count("*").alias("antall_observasjoner"),
                F.sum("antall").alias("antall_padder"),
            )
        )
    ```

## Trinn 2: Beskriv kolonnene og deklarer primærnøkkelen

Kolonnebeskrivelsene skal svare på det kolonnenavnet alene ikke sier: hva verdien betyr,
hvilken enhet den har, hvordan den er regnet ut, og hva det betyr at den mangler. Oppgi
kolonnene eksplisitt med type, `NOT NULL` og `COMMENT`, og merk kolonnen som identifiserer
raden med `PRIMARY KEY`. Nøkkelen håndheves ikke, se
[Datakvalitet](../../referanse/datakvalitet.md#constraints-og-expectations), men vises i
Catalog Explorer. Kolonnebeskrivelsene følger med som feltbeskrivelser når tabellen
publiseres til Power BI fra Catalog Explorer.

=== "SQL"

    Legg kolonnelista mellom tabellnavnet og `COMMENT`:

    ```sql
    CREATE OR REFRESH MATERIALIZED VIEW gold_default.padder_per_dag (
        dato DATE PRIMARY KEY NOT NULL COMMENT 'Dagen observasjonene ble gjort',
        antall_observasjoner BIGINT NOT NULL COMMENT 'Antall registrerte observasjoner denne dagen',
        antall_padder BIGINT NOT NULL COMMENT 'Sum av antall padder i observasjonene denne dagen'
      )
      COMMENT '...'
      AS
    SELECT
      -- som før
    ```

=== "Python"

    Legg kolonnelista i `schema` på dekoratoren:

    ```python
    @dp.materialized_view(
        name="gold_default.padder_per_dag",
        comment=BESKRIVELSE,
        schema="""
            dato DATE PRIMARY KEY NOT NULL COMMENT 'Dagen observasjonene ble gjort',
            antall_observasjoner BIGINT NOT NULL COMMENT 'Antall registrerte observasjoner denne dagen',
            antall_padder BIGINT NOT NULL COMMENT 'Sum av antall padder i observasjonene denne dagen'
        """,
    )
    def padder_per_dag():
        # som før
    ```

## Trinn 3: Deploy og kjør

Valider og deploy bundlen til stage, og kjør pipelinen. Beskrivelsene skrives til Unity
Catalog når tabellen oppdateres:

```bash
databricks bundle validate -t stage -p MY_TEAM_STAGE
databricks bundle deploy -t stage -p MY_TEAM_STAGE
databricks bundle run -t stage -p MY_TEAM_STAGE paddeobservasjoner_pipeline
```

## Bekreft resultatet

1. Åpne **Catalog Explorer**, gå til katalogen din, skjemaet `gold_default` og tabellen
   `padder_per_dag`. Fanen **Overview** skal vise beskrivelsen med formateringa,
   kolonnene med hver sin beskrivelse, og et nøkkelikon ved `dato`.
2. Kontroller det samme med SQL:

    ```sql
    SELECT column_name, data_type, comment
    FROM min_katalog.information_schema.columns
    WHERE table_schema = 'gold_default' AND table_name = 'padder_per_dag'
    ORDER BY ordinal_position;
    ```

    Alle tre kolonnene skal ha en beskrivelse.

## Endre dokumentasjonen senere

Rett teksten i pipeline-koden, deploy og kjør på nytt. Beskrivelser som er satt i koden,
skrives tilbake ved hver oppdatering, så en endring gjort i Catalog Explorer eller med
`COMMENT ON` overlever bare for felt koden ikke setter selv. Hold derfor all dokumentasjon
i koden, så svaret på hva en kolonne betyr alltid finnes i Git. Catalog Explorer kan
foreslå beskrivelser generert av KI; bruk dem gjerne som utkast, men flytt teksten inn i
koden.

## Utover Unity Catalog

Beskrivelsene dekker det en konsument trenger for å forstå og bruke tabellen. [Forslaget
til dataproduktdefinisjon](../../referanse/dataprodukt.md) stiller flere krav til et
dataprodukt, blant annet bruksrett, livssyklusstatus og tilgangsmodell, som ikke har noen
plass i tabellens metadata. Hvem som får lese tabellen, er en egen oppgave, se [Roller og
tilgangsstyring](../../om-plattformen/konsepter/roller-og-tilgangsstyring.md).

## Relatert innhold

**Guider:**

- [Skrive transformasjoner](../bearbeide-data/skrive-transformasjoner.md)

**Forklaringer:**

- [Dataprodukter](../../om-plattformen/konsepter/dataprodukter.md)
- [Eierskap og forvaltning](../../om-plattformen/konsepter/eierskap-og-forvaltning.md)

**Referanser:**

- [Definisjon av dataprodukt](../../referanse/dataprodukt.md)
- [Datakvalitet](../../referanse/datakvalitet.md)

**Ekstern dokumentasjon:**

- [Add comments to data and AI assets](https://docs.databricks.com/aws/en/comments/)
- [CREATE MATERIALIZED VIEW (pipelines)](https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-materialized-view)
- [materialized_view (Python)](https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-materialized-view)
- [Constraints on Databricks](https://docs.databricks.com/aws/en/tables/constraints)
