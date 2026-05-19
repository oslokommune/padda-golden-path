---
title: Gjenopprette etter feil i pipelines
description: Hvordan diagnostisere en feilet pipeline-kjøring og få den tilbake til fungerende tilstand i Databricks.
diataxis: how-to
---

# Gjenopprette etter feil i pipelines

Denne guiden hjelper deg å få en stoppet pipeline tilbake i drift. Vi tar utgangspunkt i en jobb eller en Declarative Pipeline som har feilet eller låst seg, og går gjennom hvordan du finner årsaken, kjører på nytt, håndterer streaming-checkpoints og bekrefter at pipelinen er frisk igjen.

## Før du begynner

Sørg for at du har:

- Tilgang til Databricks-arbeidsområdet der pipelinen kjører.
- Rettigheter til å starte og reparere kjøringer på ressursen:
  - **Jobb:** `CAN_MANAGE_RUN` for å trigge ny kjøring; `CAN_MANAGE` for å bruke **Repair run**.
  - **Declarative Pipeline:** `CAN_RUN` for å starte oppdateringer; `CAN_MANAGE` for å gjøre full refresh og endre konfigurasjon.
- Databricks CLI installert hvis du vil kjøre fra kommandolinjen. Se [Sett opp utviklingsmiljøet](../../kom-i-gang/dev-setup.md).
- Skrivetilgang til katalogen og skjemaet pipelinen skriver til, hvis du må gjøre full refresh.

## Trinn 1: Finn den feilede kjøringen

Gå til **Workflows** i Databricks-arbeidsområdet og velg fanen som matcher pipelinen din:

=== "Job"

    1. Åpne **Jobs & Pipelines** og finn jobben i listen.
    2. Klikk på jobben og åpne fanen **Runs**.
    3. Klikk inn på den feilede kjøringen (markert med rødt).

=== "Declarative Pipeline"

    1. Åpne **Jobs & Pipelines** og filtrer på pipelines.
    2. Klikk på pipelinen.
    3. Velg den siste oppdateringen (update) i listen til venstre.

Noter deg hvilket **task** eller hvilken **flow/tabell** som feilet — det er der du skal lete videre.

## Trinn 2: Diagnostiser feilen

Les feilmeldingen øverst på kjørings-/oppdateringssiden. De fleste feil havner i en av disse kategoriene:

| Symptom                                              | Sannsynlig årsak                       | Hvor du leter videre                                              |
| ---------------------------------------------------- | -------------------------------------- | ----------------------------------------------------------------- |
| `UnknownFieldException`, skjemaavvik                 | Ny eller endret kolonne i kilden       | Trinn 4                                                           |
| `AnalysisException`, type-mismatch                   | Brudd i kontrakten mellom lag          | Trinn 4                                                           |
| Timeout, `RequestTimeout`, 5xx fra ekstern API       | Forbigående nettverks- eller kildefeil | Trinn 3                                                           |
| `ConcurrentModificationException`, lås på checkpoint | Forrige kjøring ble avsluttet brått    | Trinn 5                                                           |
| Permission denied, `does not have USE CATALOG`       | Manglende rettigheter                  | [Roller og rettigheter](../../referanse/roller-og-rettigheter.md) |
| Expectation/DQX-feil                                 | Datakvalitetsbrudd                     | [Bruke DQX](./bruke-dqx.md)                                       |

For mer kontekst, se logger og event log:

=== "Job"

    Klikk på den feilede tasken og åpne **Output**, **Logs** og **Spark UI**. Driver-loggen inneholder full stacktrace.

=== "Declarative Pipeline"

    Åpne fanen **Event log** for oppdateringen. Filtrer på `ERROR` for å finne første feilende hendelse — feil i nedstrøms tabeller er ofte følgefeil av en feil lenger oppe.

Trenger du mer hjelp til logging, se [Feilsøke med logger](./logging.md).

## Trinn 3: Kjør på nytt etter en forbigående feil

Hvis feilen tyder på et forbigående problem (timeout, kildefeil, kortvarig ressursmangel), er det som regel nok å kjøre på nytt.

=== "Job (UI — repair run)"

    1. Åpne den feilede kjøringen.
    2. Klikk **Repair run**.
    3. Velg hvilke tasks som skal kjøres på nytt (som regel kun de som feilet, pluss eventuelle nedstrøms tasks).
    4. Klikk **Repair run** for å starte.

    Repair run knytter forsøkene til samme jobb-kjøring, slik at historikken samles på ett sted i stedet for å spres på flere separate kjøringer.

=== "Job (CLI)"

    `databricks bundle run` starter en ny, separat kjøring (ikke en repair av den feilede). Bruk dette når du er komfortabel med at den feilede kjøringen forblir markert som feilet i historikken:

    ```bash
    databricks bundle run <jobb> -t <target>
    ```

    Bytt ut `<jobb>` med nøkkelen fra `resources/*.yml` og `<target>` med riktig miljø.

=== "Declarative Pipeline"

    1. Åpne pipelinen.
    2. Klikk **Start** for en vanlig oppdatering.

    En vanlig start fortsetter fra siste vellykkede tilstand — den leser kun nye filer eller rader fra kilden.

!!! note
    Hvis samme feil kommer tilbake ved første reforsøk, er det sjelden forbigående. Gå tilbake til Trinn 2 og se etter en strukturell årsak før du prøver igjen.

## Trinn 4: Håndter skjemaendringer som bryter pipelinen

Når kilden får nye eller endrede kolonner, avhenger gjenopprettingen av om pipelinen er satt opp permissivt eller strikt. Se [Sette opp Auto Loader — Velg tilnærming](../hente-inn-data/auto-loader.md#trinn-1-velg-tilnrming) for bakgrunn.

=== "Permissive"

    1. Start pipelinen på nytt. Med `schemaEvolutionMode => 'addNewColumns'` feiler første kjøring som ser den nye kolonnen — Auto Loader registrerer kolonnen i schema-tilstanden, og neste start tar den med i bronse-tabellen automatisk.
    2. Hvis du vil ha med den nye kolonnen i silver/gold med historikk, kjør **Full refresh** på de tabellene som leser fra bronse:

        ```bash
        databricks pipelines start-update <pipeline_id> --full-refresh-all
        ```

        Eller via UI: **Start** → **Full refresh all** (eller **Full refresh selection** for utvalgte tabeller).

=== "Strict"

    1. Oppdater `schema`-parameteren i `read_files()` og kolonnelisten i de relevante `CREATE OR REFRESH STREAMING TABLE`-setningene slik at de matcher kilden.
    2. Deploy bundlen på nytt:

        ```bash
        databricks bundle deploy -t <target>
        ```

    3. Kjør **Full refresh** på de tabellene du har endret skjema på. Streaming-tabellen er deklarert med eksplisitt kolonneliste, så en endret skjemadefinisjon krever at tabellen bygges på nytt:

        ```bash
        databricks pipelines start-update <pipeline_id> --full-refresh-all
        ```

!!! warning "Full refresh sletter og bygger tabellen på nytt"
    Alle rader regenereres fra kilden. Sørg for at kilden fortsatt har all data du trenger, og varsle nedstrøms forbrukere før du starter.

## Trinn 5: Resett en låst streaming-checkpoint

En streaming-jobb (eller en streaming-tabell i en Declarative Pipeline) som ble avsluttet brått midt i en commit, kan etterlate seg en checkpoint-tilstand som blokkerer ny progresjon. Symptomer er gjerne `ConcurrentModificationException`, melding om at en batch allerede er committet, eller en stream som henger i `INITIALIZING` uten å produsere data.

=== "Declarative Pipeline"

    Kjør **Full refresh** på den aktuelle streaming-tabellen. Pipelinen oppretter ny checkpoint-tilstand fra bunn:

    ```bash
    databricks pipelines start-update <pipeline_id> --full-refresh <table_name>
    ```

=== "Egen streaming-jobb"

    1. Stopp jobben slik at ingen kjøringer er aktive.
    2. Slett (eller flytt) checkpoint-mappen. Plattformen bruker Unity Catalog Volumes for slik tilstand:

        ```bash
        databricks fs rm -r dbfs:/Volumes/<katalog>/<skjema>/<volum>/checkpoints/<stream_navn>
        ```

        Hvis pipelinen din fortsatt skriver checkpoint til legacy-DBFS (`dbfs:/path/...`), gjelder samme kommando med riktig sti.

    3. Start jobben på nytt. Streamen leser fra start, eller fra konfigurert startposisjon (`cloudFiles.includeExistingFiles` for Auto Loader, `startingVersion` / `startingTimestamp` for Delta-kilder).

!!! warning "Sletting av checkpoint er irreversibelt"
    Streamen mister kunnskapen om hvilke filer/rader som er behandlet. For Auto Loader betyr det at alle filer i kildeområdet leses inn på nytt — det kan gi duplikater hvis nedstrøms tabeller ikke er idempotente. Bruk full refresh i stedet når mulig.

## Bekreft resultatet

Kontroller at pipelinen er frisk igjen:

1. **Status:** Siste kjøring/oppdatering står som `Succeeded` i **Workflows**.
2. **Data:** Spør tabellene pipelinen skriver til, og verifiser at radantallet og siste tidsstempel er som forventet (forutsetter at tabellen har en `ingested_at`-kolonne — bundle-malene legger denne på automatisk):

   ```sql
   SELECT
     COUNT(*) AS row_count,
     MAX(ingested_at) AS last_ingested
   FROM min_katalog.bronze_default.min_tabell;
   ```

3. **Schedule:** Hvis pipelinen kjører på schedule, vent til neste planlagte kjøring og bekreft at den også går grønt — eller trigg en ny kjøring manuelt.
4. **Varsler:** Sjekk at eventuelle alarmer har clearet. Se [Sette opp Slack-alarmer](./slack-alarmer.md).

## Feilsøking

??? failure "Pipeline starter, men feiler umiddelbart med samme feil"
    Endringene dine er sannsynligvis ikke deployet.

    Løsning:

    - Kjør `databricks bundle deploy -t <target>` på nytt og bekreft at outputen viser den oppdaterte filen.
    - For Declarative Pipelines: åpne **Settings** og verifiser at SQL/Python-stiene peker på den oppdaterte versjonen.

??? failure "`Full refresh` etterlater nedstrøms tabeller tomme"
    En full refresh på en oppstrøms tabell uten å inkludere nedstrøms tabeller bryter avhengighetene.

    Løsning:

    - Kjør **Full refresh all**, eller velg alle tabeller som er nedstrøms av den du refreshet.

??? failure "`Repair run` er nedtonet i UI-et"
    Repair run er kun tilgjengelig for kjøringer som har feilet eller blitt avbrutt.

    Løsning:

    - For en kjøring som står som `Succeeded` (men med feil i innholdet): trigg en ny kjøring med **Run now** eller `databricks bundle run`.

??? failure "Streaming-jobben starter, men leser ingen nye filer"
    Auto Loader bruker checkpointet til å huske hvilke filer som er sett. Hvis checkpointet peker på en tom eller utdatert tilstand, kan streamen stå stille.

    Løsning:

    - Sjekk **Streaming-fanen** i Spark UI for `numFilesOutstanding`.
    - Hvis tallet er 0 og du forventer nye filer, verifiser at filene faktisk ligger i kildestien og at stien matcher `read_files(...)`-mønsteret.

## Relatert innhold

- [Feilsøke med logger](./logging.md)
- [Sette opp Auto Loader](../hente-inn-data/auto-loader.md)
- [Bruke DQX](./bruke-dqx.md)
- [Declarative Automation Bundles](../../referanse/databricks-bundles.md)
- [Databricks-dokumentasjon: Repair an unsuccessful job run](https://docs.databricks.com/aws/en/jobs/repair-job-failures)
- [Databricks-dokumentasjon: Run a pipeline update](https://docs.databricks.com/aws/en/dlt/updates)
