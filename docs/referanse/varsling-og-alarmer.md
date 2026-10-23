---
title: Varsling og alarmer
description: Varslingskanaler, varsler på jobber og pipelines, SQL-alarmer, ferskhetsvarselet fra bundle-malen og feltene som konfigurerer dem i bundlen.
diataxis: reference
---

# Varsling og alarmer

Plattformen har fire måter å varsle på: varsler fra jobber, varsler fra pipelines,
SQL-alarmer og ferskhetsvarselet fra bundle-malen. Teamet setter opp alle fire selv, i
[bundlen](databricks-bundles.md) sammen med ressursen de gjelder. Hvorfor ansvaret er
delt slik, står det om i [Overvåking](../om-plattformen/konsepter/overvaaking.md).

## Varslingskanaler

Et varsel sendes på e-post eller til en *notification destination*. E-postadresser skriver
du rett inn i konfigurasjonen til jobben, pipelinen eller alarmen. En notification
destination er et objekt i workspacet som lagrer det som trengs for å nå en annen kanal,
for eksempel en Slack-webhook.

Notification destinations opprettes og endres av en
[workspace-admin](roller-og-rettigheter.md#workspace-admin), det vil si teamets egen
admingruppe. Når destinasjonen finnes, kan alle i workspacet bruke den. Konfigurasjonen
lagres kryptert i workspacet. Jobber, pipelines og alarmer peker på destinasjonen med
ID-en dens, som du finner med `databricks notification-destinations list`. I en bundle kan
en variabel slå opp ID-en fra navnet med `lookup: notification_destination`. Se
[Sette opp Slack-varsler](../guider/overvaake-og-drifte/slack-varsler.md) for oppsettet.

## Varsler på jobber

En jobb sender varsler ved hendelser i kjøringen. Varslene konfigureres i to felt på
jobben: `email_notifications` sender e-post, og `webhook_notifications` sender til
notification destinations, inntil tre per hendelse. Hendelsene er:

| Hendelse                                 | Utløses når                                                               |
|------------------------------------------|---------------------------------------------------------------------------|
| `on_start`                               | Kjøringen starter                                                         |
| `on_success`                             | Kjøringen fullfører uten feil                                             |
| `on_failure`                             | Kjøringen feiler                                                          |
| `on_duration_warning_threshold_exceeded` | Kjøringen har vart lenger enn regelen `RUN_DURATION_SECONDS` tillater     |
| `on_streaming_backlog_exceeded`          | En strøm har større etterslep enn en `STREAMING_BACKLOG_*`-regel tillater |

De to siste hendelsene krever at jobben har en regel under `health.rules`. En regel sier
at en metrikk ikke skal overstige en terskel, med operatoren `GREATER_THAN` og en verdi.
`RUN_DURATION_SECONDS` måler kjøretiden i sekunder. Metrikkene for etterslep i strømmer,
`STREAMING_BACKLOG_*`, er beskrevet i [Add notifications on a
job](https://docs.databricks.com/aws/en/jobs/notifications).

Under `notification_settings` kan du begrense varslene:

| Felt                         | Virkning                                                                                  |
|------------------------------|-------------------------------------------------------------------------------------------|
| `no_alert_for_skipped_runs`  | Ingen varsel når en kjøring hoppes over                                                   |
| `no_alert_for_canceled_runs` | Ingen varsel når en kjøring avbrytes                                                      |
| `alert_on_last_attempt`      | Venter med varsel til siste forsøk har feilet, for tasks som prøver på nytt med `retries` |

Alle feltene kan stå på jobben eller på hver enkelt task. Et varsel på jobben sendes én
gang per kjøring, selv om en task feiler og prøves på nytt flere ganger underveis. Et
varsel på tasken sendes for hvert enkelt feilede forsøk.

Eksempel på en jobb som sender e-post ved feil og lang kjøretid, og i tillegg varsler i
Slack ved feil:

```yaml
resources:
  jobs:
    paddeobservasjoner:
      name: paddeobservasjoner
      email_notifications:
        on_failure:
          - padda@example.org
        on_duration_warning_threshold_exceeded:
          - padda@example.org
      webhook_notifications:
        on_failure:
          - id: ${var.slack_destination_id}
      health:
        rules:
          - metric: RUN_DURATION_SECONDS
            op: GREATER_THAN
            value: 3600
      notification_settings:
        no_alert_for_skipped_runs: true
```

Destinasjonen har ulik ID i hvert workspace. Derfor settes ID-en som en variabel per
target i `databricks.yml`.

## Varsler på pipelines

En pipeline har egne varsler under `notifications`, uavhengig av jobben som eventuelt
kjører den. Hvert varsel har en liste med e-postadresser i `email_recipients` og en liste
med hendelser i `alerts`:

| Hendelse                  | Utløses når                                                         |
|---------------------------|---------------------------------------------------------------------|
| `on-update-success`       | En oppdatering fullfører uten feil                                  |
| `on-update-failure`       | En oppdatering feiler, også når pipelinen prøver på nytt automatisk |
| `on-update-fatal-failure` | En oppdatering feiler for godt, uten nytt forsøk                    |
| `on-flow-failure`         | Én enkelt flyt i pipelinen feiler                                   |

```yaml
resources:
  pipelines:
    paddeobservasjoner:
      name: paddeobservasjoner
      notifications:
        - email_recipients:
            - padda@example.org
          alerts:
            - on-update-fatal-failure
            - on-flow-failure
```

Pipelinevarsler kan bare gå på e-post. Kjører pipelinen som en task i en jobb, feiler
jobben når pipelinen feiler, og jobbens varsler sendes. Det er slik en feilet pipeline når
Slack.

## SQL-alarmer

En SQL-alarm, *SQL alert* i Databricks, er en [SQL-spørring som kjører på
tidsplan](https://docs.databricks.com/aws/en/sql/user/alerts/) mot et [SQL
Warehouse](sql-warehouse.md), og som varsler når resultatet bryter en betingelse, for
eksempel at data ikke kom, eller at en karantenetabell har fått nye rader.

En alarm består av:

| Del                              | Innhold                                                                                                                              |
|----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| `query_text`                     | Spørringen som kjøres. Den hører til alarmen og kan ikke ha parametere                                                               |
| `warehouse_id`                   | Warehouset spørringen kjører på                                                                                                      |
| `evaluation.source`              | Kolonnen som evalueres, eventuelt med en aggregering: `SUM`, `COUNT`, `COUNT_DISTINCT`, `AVG`, `MEDIAN`, `MIN`, `MAX` eller `STDDEV` |
| `evaluation.comparison_operator` | `GREATER_THAN`, `GREATER_THAN_OR_EQUAL`, `LESS_THAN`, `LESS_THAN_OR_EQUAL`, `EQUAL`, `NOT_EQUAL`, `IS_NULL` eller `IS_NOT_NULL`      |
| `evaluation.threshold`           | Verdien kolonnen sammenlignes med: et tall, en tekst, en boolsk verdi eller en annen kolonne                                         |
| `evaluation.empty_result_state`  | Tilstanden alarmen får når spørringen ikke returnerer rader: `OK`, `TRIGGERED` eller `ERROR`                                         |
| `evaluation.notification`        | Mottakere i lista `subscriptions`, som `user_email` eller `destination_id`, og innstillingene `notify_on_ok` og `retrigger_seconds`  |
| `schedule`                       | Tidsplan som cron-uttrykk (Quartz) med tidssone                                                                                      |

Hver gang alarmen kjører, får den tilstanden `OK`, `TRIGGERED` eller `ERROR`. Varsel
sendes når alarmen blir `TRIGGERED`. `retrigger_seconds` er minste antall sekunder mellom
to varsler mens alarmen fortsatt er utløst. Med `notify_on_ok` får du også varsel når
alarmen går tilbake til `OK`.

Alarmer defineres som ressursen `alerts` i bundlen. Eksemplet under varsler når
karantenetabellen fra [Håndtere rader som ikke lar seg
konvertere](../guider/bearbeide-data/haandtere-ugyldige-rader.md) har fått nye rader det
siste døgnet:

```yaml
resources:
  alerts:
    karantene_nye_rader:
      display_name: Nye rader i karantene for paddeobservasjoner
      warehouse_id: ${var.warehouse_id}
      query_text: |
        SELECT *
        FROM ${var.catalog}.silver_default.paddeobservasjoner_karantene
        WHERE lagt_i_karantene > current_timestamp() - INTERVAL 1 DAY
      evaluation:
        source:
          name: observasjon_id
          aggregation: COUNT
        comparison_operator: GREATER_THAN
        threshold:
          value:
            double_value: 0
        empty_result_state: OK
        notification:
          subscriptions:
            - user_email: padda@example.org
            - destination_id: ${var.slack_destination_id}
      schedule:
        quartz_cron_schedule: 0 0 7 * * ?
        timezone_id: Europe/Oslo
```

Spørringen kjører som identiteten i `run_as`, som må ha lesetilgang til tabellene den spør
mot. En alarm kan også evalueres av en egen task i en jobb, for eksempel rett etter
pipelinen som fyller tabellen. Tasken evaluerer alarmen når jobben kjører, mens alarmens
egen tidsplan fortsetter uavhengig. Se [SQL alert task for
jobs](https://docs.databricks.com/aws/en/jobs/tasks/alert).

## Ferskhetsvarsel

Ferskhetsvarselet er en jobb fra bundle-malen som feiler når en overvåket tabell ikke har
fått nye data innenfor ferskhetsgrensen sin. Feilen varsles som for andre jobber, med
`webhook_notifications`. Oppsettet står i [Sette opp
ferskhetsvarsel](../guider/overvaake-og-drifte/ferskhetsvarsel.md).

### Malvalget `include_freshness_alert`

| Egenskap    | Verdi |
|-------------|-------|
| Verdier     | `no` (standard), `yes` |
| Spørres når | `setup_type` er `default` eller `tailored`; aldri for `minimal` |
| Legger til  | Jobben `freshness_alert` i `resources/freshness_alert.job.yml`, pakken `src/<pakke>/freshness/`, testene `tests/test_freshness.py`, entry point `freshness_alert`, og variabelen `slack_destination_id` i `databricks.yml` |

`slack_destination_id` slår opp destinasjonen med navnet `REPLACE_WITH_DESTINATION_NAME` i
både `stage` og `prod`, så `databricks bundle validate` og `deploy` feiler til navnet er
byttet ut.
Med eksempeljobbene overvåker den genererte jobben tabellen `bronze_nyctaxi` fra
eksempelpipelinen. Uten eksempeljobbene (`include_example_jobs: no`) overvåker den en
plassholder, `TODO_table`, som ikke kan sjekkes før den er byttet ut.

### Jobben

| Felt         | Verdi                                                                                                         |
|--------------|---------------------------------------------------------------------------------------------------------------|
| Compute      | Serverless, miljøversjon 5                                                                                    |
| Tidsplan     | Hver dag kl. 07:00 (`quartz_cron_expression: "0 0 7 * * ?"`), på pause som standard                           |
| Varsling     | `webhook_notifications.on_failure` til `${var.slack_destination_id}`, med `no_alert_for_skipped_runs: true` |
| E-post       | Ingen                                                                                                         |
| Tidsavbrudd  | 600 sekunder for tasken                                                                                       |
| Kjører som   | `run_as` på targeten: service principalen i prod, den som deployer i stage                                    |

Tidsplanen har `pause_status: PAUSED`, så jobben kjører bare når noen starter den. Med
`pause_status: UNPAUSED` kjører den etter tidsplanen i både stage og prod, selv om
stage-targeten har `mode: development`. Feil i stage varsler `slack_destination_id` for
stage-targeten.

Hver kjøring som finner et problem, sender ett varsel. Med daglig tidsplan blir det ett
varsel per dag til problemet er løst.

### Overvåkede tabeller

Hver overvåket tabell er én parameter på tasken, med tre verdier skilt av mellomrom:

```text
<fullt tabellnavn> <kolonne med innlastingstidspunkt> <ferskhetsgrense>
```

```yaml
parameters:
  - ${var.catalog}.${var.schema}.bronze_nyctaxi load_date 25h
  - ${var.catalog}.${var.schema}.raw_nyctaxi load_date 25h
```

- Alle tre verdiene er påkrevd. Det finnes ingen standardverdier.
- Tabellnavnet er fullt kvalifisert, `katalog.skjema.tabell`. Med `${var.catalog}` peker
  stage og prod på hver sin katalog.
- Kolonnen med innlastingstidspunkt må ha typen `TIMESTAMP`. En kolonne av typen `DATE`
  eller `TIMESTAMP_NTZ` kan ikke sjekkes.
- Ferskhetsgrensen er et positivt heltall fulgt av `m` (minutter), `h` (timer) eller `d`
  (døgn), for eksempel `30m`, `25h` eller `8d`.

En parameter som ikke har nøyaktig tre verdier, eller som har en ugyldig ferskhetsgrense,
feiler jobben før noen tabell er sjekket. Feilmeldingen siterer parameteren.

### Måling og utfall

Dataferskheten er tiden fra det nyeste innlastingstidspunktet i tabellen,
`max(<kolonne>)`, til nå, regnet i UTC.

| Situasjon                                                                              | Utfall                                                |
|----------------------------------------------------------------------------------------|-------------------------------------------------------|
| Dataferskheten er innenfor ferskhetsgrensen                                            | OK                                                    |
| Dataferskheten er større enn ferskhetsgrensen                                          | For gamle data, under `Stale` i feilmeldingen         |
| Tabellen er tom (`max()` er NULL)                                                      | For gamle data, rapportert som `no rows`              |
| Tabellen eller kolonnen finnes ikke, kolonnen har feil type, eller lesetilgang mangler | Kan ikke sjekkes, under `Could not check` med årsaken |

Jobben sjekker alle tabellene før den rapporterer. For hver tabell logger den én
INFO-linje med navn, nyeste innlastingstidspunkt, alder og ferskhetsgrense, også når alle
er OK. Har minst én tabell et problem, feiler jobben med én feilmelding som lister alle
problemene, én linje per tabell. Tabeller med for gamle data og tabeller som ikke kan
sjekkes, står i hver sin liste.

Slack-meldingen sier bare at jobben feilet, med teksten `Task freshness_alert failed with
message: Workload failed, see run output for details.` Hvilke tabeller som har problemer,
står i kjøreresultatet (*run output*) til kjøringen.

### Begrensninger

- **Full refresh.** En full refresh skriver innlastingstidspunktet på nytt for alle rader,
  også når kilden ikke har nye data. Tabellen ser da fersk ut, og varselet går ikke før
  ferskhetsgrensen er passert på nytt.
- **Bare tabeller med kolonne med innlastingstidspunkt.** En tabell uten en slik kolonne
  kan ikke overvåkes. Se [Sette opp
  ferskhetsvarsel](../guider/overvaake-og-drifte/ferskhetsvarsel.md#legge-til-en-kolonne-med-innlastingstidspunkt).
- **Bare nye bundles.** Valget finnes i bundle-malen og legges ikke inn i bundles som
  allerede er generert.

## Relatert innhold

**Forklaringer:**

- [Overvåking](../om-plattformen/konsepter/overvaaking.md) — hvorfor varsling er teamets
  ansvar

**Guider:**

- [Sette opp Slack-varsler](../guider/overvaake-og-drifte/slack-varsler.md) — opprette en
  notification destination for Slack
- [Sette opp ferskhetsvarsel](../guider/overvaake-og-drifte/ferskhetsvarsel.md) — ta i
  bruk ferskhetsvarselet i en bundle generert med `include_freshness_alert: yes`
- [Feilsøke med logger](../guider/overvaake-og-drifte/logging.md) og [Gjenopprette etter
  feil i pipelines](../guider/overvaake-og-drifte/gjenopprette-etter-feil.md) — når
  varselet har kommet
- [Håndtere rader som ikke lar seg
  konvertere](../guider/bearbeide-data/haandtere-ugyldige-rader.md) — karantenetabellen
  fra alarmeksemplet

**Referanser:**

- [Datakvalitet](datakvalitet.md) — expectations og DQX, som lar kvalitetssjekker feile
  jobben
- [SQL Warehouse](sql-warehouse.md) — warehousene alarmer kjører på
- [Declarative Automation Bundles](databricks-bundles.md) — der konfigurasjonen bor

**Ekstern dokumentasjon:**

- [Add notifications on a job](https://docs.databricks.com/aws/en/jobs/notifications)
- [Manage notification destinations](https://docs.databricks.com/aws/en/admin/workspace-settings/notification-destinations)
- [Pipelines API: notifications](https://docs.databricks.com/api/workspace/pipelines/create)
- [Alerts V2 API](https://docs.databricks.com/api/workspace/alertsv2/createalert)
