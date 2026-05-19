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
    2. Filtrer på **Run status: Failed** eller åpne jobben og se **Runs**-fanen.
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

På siden **Task run details** finner du panelet til høyre med lenker til loggene.
Driveren skriver tre strømmer som er nyttige i ulike situasjoner:

- **`stdout`** — alt som er skrevet med `print()` eller bibliotek som logger til standard ut.
- **`stderr`** — Python-stacktraces, advarsler og det meste fra `logging`-biblioteket havner her.
- **`log4j`** — Spark sine egne meldinger om jobber, stages, tasks og executors.

For notebook-tasks som returnerer en verdi via `dbutils.notebook.exit(...)` kan
du også hente returverdien direkte:

```bash
databricks jobs get-run-output <RUN_ID>
```

!!! note

    For serverless compute eksponeres ikke `log4j`-fanen og Spark UI på samme måte
    som for klassisk compute. Bruk **Query profile** og **Metrics**-fanen i jobb-UI-et
    for ytelses- og spørringsdetaljer.

For dypere undersøkelser av Spark-jobben, klikk **Spark UI** fra task-detaljsiden
for å se stages, tasks, shuffle-statistikk og executor-logger per node.

## Trinn 3: Tolk vanlige feilmeldinger

Lokaliser stacktracen i `stderr` og finn rotårsaken:

- Den **innerste** `Caused by:`-linjen er som regel rotårsaken.
- Spark-feil starter ofte med `Py4JJavaError` eller `SparkException` på toppen,
  men den faktiske årsaken (f.eks. `AnalysisException`, `FileNotFoundException`,
  `OutOfMemoryError`) ligger lenger ned.
- For tasks som feilet under utførelse av en Spark-jobb, søk etter
  `Job aborted due to stage failure` i `log4j` og bla oppover til den første
  failed task — den inneholder ofte mer kontekst enn drivermeldingen.

!!! tip

    I Jobs UI kan du klikke **Diagnose Error** for å la **Genie Code** foreslå
    en sannsynlig årsak basert på feilmeldingen. Bruk det som utgangspunkt —
    verifiser alltid mot den faktiske stacktracen før du gjør endringer.

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
    databricks jobs repair-run <RUN_ID> --rerun-tasks <TASK_KEY>,<TASK_KEY>
    ```

!!! note

    - Repair krever at jobben har minst to tasks.
    - Hvis flere tasks deler et `job_cluster`, opprettes et nytt cluster med
      versjonssuffiks (f.eks. `my_job_cluster_v1`) slik at du i ettertid kan se
      hvilken konfigurasjon som ble brukt i hver kjøring.
    - Repair bruker hver tasks **run state**, ikke deres `disabled`-status.
      For å tvinge en deaktivert task med i en repair, må den eksplisitt listes
      i `rerun_tasks`.

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

    Ikke logg hemmeligheter, persondata eller hele rader fra datasett. Logger fra
    driveren kan ende opp i langtidslagring (se Trinn 6) og være tilgjengelige for
    flere enn de som har tilgang til selve dataene.

## Trinn 6: Lever logger til varig lagring (valgfritt)

Driver-logger forsvinner når compute-ressursen termineres. For jobber som kjører
på `new_cluster` (klassisk compute) kan du levere logger kontinuerlig til et
Unity Catalog-volum ved å sette `cluster_log_conf` i bundlen:

```yaml
job_clusters:
  - job_cluster_key: job_cluster
    new_cluster:
      spark_version: 17.3.x-scala2.13
      node_type_id: i3.xlarge
      data_security_mode: SINGLE_USER
      cluster_log_conf:
        volumes:
          destination: /Volumes/<katalog>/<skjema>/<volum>
```

Databricks leverer logger hvert 5. minutt og arkiverer dem hver time under
`<destination>/<cluster_id>/` i undermappene `driver/`, `executor/`, `eventlog/`
og (hvis aktuelt) `init_scripts/`. Owner eller assigned user på compute må ha
`READ VOLUME` og `WRITE VOLUME` på volumet.

!!! note

    Logglevering til volum krever Unity Catalog-aktivert compute med tilgangsmodus
    **Standard** eller **Dedicated** (tilordnet en bruker). Det støttes ikke for
    serverless eller for **Dedicated** tilordnet en gruppe. Funksjonen er i
    Public Preview.

!!! tip

    Sett `cluster_log_conf` som **fixed value** i en cluster policy slik at
    teamet ikke kan glemme å slå det på. Da treffer alle nye job clusters samme
    volum uten ekstra konfigurasjon i bundlen.

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
    - Tasken kjører på serverless compute. Da eksponeres ikke `log4j`-fanen og
      Spark UI på samme måte.
    - Compute ble terminert før loggene ble levert til varig lagring.

    Løsning:

    - Be en admin om tilgang, eller bytt til **Dedicated** access mode hvis du
      trenger å lese loggene selv.
    - For serverless: bruk `logger.info(...)` til `stderr`, **Metrics**-fanen og
      **Query profile** framfor å lete etter `log4j`-filer.
    - For klassisk compute: aktiver `cluster_log_conf` (se Trinn 6) slik at
      logger persisteres utenfor compute-livssyklusen.

??? failure "`Py4JJavaError` uten meningsfull årsak"

    Sannsynlig årsak: den faktiske feilen kommer fra en executor og er ikke
    fullstendig propagert til driveren.

    Løsning:

    1. Åpne **Spark UI** fra task-detaljsiden.
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
- [Sette opp Slack-alarmer](slack-alarmer.md)
- [Varsling og alarmer](../../referanse/varsling-og-alarmer.md)
- [Monitoring and observability for Lakeflow Jobs (Databricks-dokumentasjon)](https://docs.databricks.com/aws/en/jobs/monitor)
- [Troubleshoot and repair job failures (Databricks-dokumentasjon)](https://docs.databricks.com/aws/en/jobs/repair-job-failures)
- [Debugging with the Spark UI (Databricks-dokumentasjon)](https://docs.databricks.com/aws/en/compute/troubleshooting/debugging-spark-ui)
