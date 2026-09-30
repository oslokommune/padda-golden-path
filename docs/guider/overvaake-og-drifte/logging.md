---
title: Feilsøke med logger
description: Hvordan finne, lese og berike Databricks-logger for å diagnostisere problemer i pipelines.
diataxis: how-to
---

# Feilsøke med logger

Denne veiledningen viser hvordan du finner logger for en feilet jobbkjøring,
tolker driver- og Spark-loggene, beriker egne notebooks med logging og
verifiserer at problemet er løst etter en endring. Et vellykket resultat er at
du kan peke på den konkrete linjen i loggen som forklarer feilen og bekrefte at
en ny kjøring går grønt.

## Før du begynner

Sørg for at du har:

- Tilgang til Databricks-arbeidsområdet hvor jobben kjører
- `CAN_VIEW`-tilgang (eller høyere) på jobben det gjelder
- `databricks` CLI installert og autentisert (kun nødvendig for CLI-trinnene)
- Run-ID eller jobbnavn for kjøringen du skal feilsøke

!!! note

    Databricks oppbevarer kjørehistorikk i 60 dager. Eldre kjøringer må eksporteres
    før de utløper hvis du trenger dem til etterforskning.

## Trinn 1: Finn den feilede kjøringen

=== "UI"

    1. Klikk **Jobs & Pipelines** i venstremenyen.
    2. Se **Runs**-fanen og filtrer på **Run status: Failed** eller åpne jobben og se **Runs**-fanen der inne.
    3. Klikk lenken i **Start time**-kolonnen for å åpne kjøringsdetaljene.
    4. I grafvisningen er feilede tasks røde — klikk noden for tasken som feilet.

=== "CLI"

    List de siste kjøringene for en jobb:

    ```bash
    databricks jobs list-runs --job-id <JOB_ID> --completed-only --limit 10
    ```

    Hent metadata for én kjøring (inkludert `state.result_state` og `state.state_message`):

    ```bash
    databricks jobs get-run <RUN_ID>
    ```

## Trinn 2: Les driver- og Spark-loggene

På panelet til høyre finner du **Compute** med lenker til loggene.
Driveren skriver tre strømmer som er nyttige i ulike situasjoner:

- **`stderr`** — start her. Python-stacktraces og `logging`-utdata.
- **`stdout`** — `print()`-utdata.
- **`log4j`** — Spark-meldinger om jobber, stages, tasks og executors.

For notebook-tasks som returnerer en verdi via `dbutils.notebook.exit(...)` kan
du også hente returverdien direkte:

```bash
databricks jobs get-run-output <RUN_ID>
```

!!! note

    For serverless compute eksponeres ikke Spark UI på samme måte
    som for klassisk compute.

For dypere undersøkelser av Spark-jobben, klikk **Spark UI** fra compute-siden
for å se stages, tasks, shuffle-statistikk og executor-logger per node.

## Trinn 3: Finn rotårsaken i stacktracen

Lokaliser stacktracen i `stderr` og finn rotårsaken:

- Les fra bunnen av stacktracen — den **innerste** `Caused by:`-linjen er som
  regel rotårsaken.
- Hopp over `Py4JJavaError` og `SparkException` på toppen og let etter konkrete
  unntak som `AnalysisException`, `FileNotFoundException` eller
  `OutOfMemoryError`.
- Ved `Job aborted due to stage failure`, åpne `log4j` og bla opp til den
  første failed task — den har ofte mer kontekst enn drivermeldingen.

!!! tip

    I Jobs UI kan du klikke **Diagnose Error** for å la **Genie Code** foreslå
    en sannsynlig årsak basert på feilmeldingen.

## Trinn 4: Reparer i stedet for å kjøre alt på nytt

For multi-task-jobber er **Repair run** raskere og billigere enn å kjøre hele
jobben på nytt — kun feilede tasks og deres avhengige tasks kjøres igjen.
Vellykkede tasks gjenbrukes som de er.

=== "UI"

    1. Åpne den feilede kjøringen fra **Runs**-fanen.
    2. Klikk **Repair run** øverst på siden.
    3. Dialogen lister alle tasks som vil kjøres på nytt. Eventuelt overstyr
       parametere i dialogen — disse vinner over eksisterende verdier kun for
       denne reparasjonen.
    4. Klikk **Repair run** for å starte.

=== "CLI"

    ```bash
    databricks jobs repair-run <RUN_ID> --rerun-all-failed-tasks
    ```

!!! note

    - Repair krever at jobben har minst to tasks.
    - Hvis flere tasks deler et `job_cluster`, opprettes et nytt cluster med
      versjonssuffiks (f.eks. `my_job_cluster_v1`) slik at du i ettertid kan se
      hvilken konfigurasjon som ble brukt i hver kjøring.
    - Repair bruker hver tasks **run state**, ikke deres `disabled`-status.
      For å tvinge en deaktivert task med i en repair, må den eksplisitt listes
      i `rerun_tasks`. Fra CLI gjøres det med
      `--json '{"rerun_tasks": ["<TASK_KEY>"]}'` i stedet for
      `--rerun-all-failed-tasks`.

Se [Gjenopprette etter feil i pipelines](gjenopprette-etter-feil.md) for andre
scenarier (forbigående feil, låste streaming-checkpoints, schema-endringer).

## Trinn 5: Legg til logging i egne notebooks

Bruk Pythons standardbibliotek `logging` framfor `print()` — da får du nivåer,
tidsstempel og modulnavn i `stderr`:

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.info("Leser %d rader fra %s", df.count(), source_path)  # (1)!
logger.warning("Fant %d duplikater på primærnøkkel", duplicates)
try:
    df.write.saveAsTable(target)
except Exception:
    logger.exception("Skriv til %s feilet", target)  # (2)!
    raise
```

1. Bruk lazy formatting (`%s`, `%d`) i stedet for f-strings — da hopper
   `logging` over selve strengformateringen når loggnivået er deaktivert.
2. `logger.exception(...)` legger automatisk til full stacktrace — bruk den
   inne i `except`-blokker.

!!! warning

    Ikke logg hemmeligheter, persondata eller hele rader fra datasett.

## Bekreft resultatet

Etter at du har gjort en endring og deployet på nytt, kjør jobben og bekreft at:

```bash
databricks jobs run-now <JOB_ID>
databricks jobs list-runs --job-id <JOB_ID> --limit 1
```

Forventet utdata fra `list-runs` viser den nye kjøringen med
`result_state: SUCCESS`:

```text
ID         Start Time           ...  Status     Result State
123456789  2025-01-15 09:12:03  ...  TERMINATED SUCCESS
```

Åpne kjøringen i UI-et og kontroller at:

- Alle leaf tasks er grønne i grafvisningen.
- Loggmeldingene du la til i Trinn 5 dukker opp i `stderr` med riktig nivå.
- Feilmeldingen fra Trinn 3 ikke lenger forekommer i loggen.

## Feilsøking

??? failure "Loggene er tomme eller mangler `log4j`"

    Sannsynlige årsaker:

    - Du er ikke workspace admin på en compute med tilgangsmodus **Standard**.
      Da kan kun admins se driver-logger, og executor-logger er ikke
      tilgjengelige i det hele tatt. På **Dedicated** access mode kan tilordnet
      bruker/gruppe og admins se loggene.
    - Tasken kjører på serverless compute. Da eksponeres ikke
      Spark UI på samme måte.
    - Compute ble terminert før loggene ble levert til varig lagring.

    Løsning:

    - Be en admin om tilgang, eller bytt til **Dedicated** access mode hvis du
      trenger å lese loggene selv.
    - For serverless: bruk `logger.info(...)` til `stderr`, **Metrics**-fanen og
      **Query profile** framfor å lete etter `log4j`-filer.

??? failure "`Py4JJavaError` uten meningsfull årsak"

    Sannsynlig årsak: den faktiske feilen kommer fra en executor og er ikke
    fullstendig propagert til driveren.

    Løsning:

    1. Åpne **Spark UI** fra compute-siden.
    2. Gå til **Stages**-fanen og finn stagen markert som **Failed**.
    3. Åpne den første failed tasken og noter **Task ID** og **Executor ID**.
    4. Gå til **Executors**-fanen og åpne loggene for den aktuelle executoren
      — stacktracen ligger ofte der, ikke på driveren.
    5. Hvis tasken henger i stedet for å feile, klikk **Thread Dump** for
      executoren og finn tråden med `TID <Task ID>` for å se hva den venter på.

??? failure "`logger.info(...)` vises ikke i `stderr`"

    Sannsynlig årsak: rot-loggeren er konfigurert med et høyere nivå enn `INFO`,
    eller du har laget en logger uten å sette nivå.

    Løsning:

    - Sett `logger.setLevel(logging.INFO)` eksplisitt på din egen logger, eller
    - Konfigurer roten én gang øverst i notebooken:
      `logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")`.

## Relatert innhold

- [Gjenopprette etter feil i pipelines](gjenopprette-etter-feil.md)
- [Sette opp Slack-varsler](slack-varsler.md)
- [Varsling og alarmer](../../referanse/varsling-og-alarmer.md)
- [Monitoring and observability for Lakeflow Jobs (Databricks-dokumentasjon)](https://docs.databricks.com/aws/en/jobs/monitor)
- [Troubleshoot and repair job failures (Databricks-dokumentasjon)](https://docs.databricks.com/aws/en/jobs/repair-job-failures)
- [Debugging with the Spark UI (Databricks-dokumentasjon)](https://docs.databricks.com/aws/en/compute/troubleshooting/debugging-spark-ui)
