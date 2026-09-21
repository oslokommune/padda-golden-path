---
title: Varsling og alarmer
description: Varslingskanaler, varsler på jobber og pipelines, SQL-alarmer og feltene som konfigurerer dem i bundlen.
diataxis: reference
---

# Varsling og alarmer

Plattformen har tre måter å varsle på: varsler fra jobber, varsler fra pipelines og
SQL-alarmer. Teamet setter opp alle tre selv, i [bundlen](databricks-bundles.md) sammen
med ressursen de gjelder. Hvorfor ansvaret er delt slik, står det om i
[Overvåking](../om-plattformen/konsepter/overvaaking.md).

## Varslingskanaler

Et varsel sendes på e-post eller til en *notification destination*. E-postadresser skriver
du rett inn i konfigurasjonen til jobben, pipelinen eller alarmen. En notification
destination er et objekt i workspacet som lagrer det som trengs for å nå en annen kanal,
for eksempel en Slack-webhook.

Notification destinations opprettes og endres av en
[workspace-admin](roller-og-rettigheter.md#workspace-admin), det vil si teamets egen
admingruppe. Når destinasjonen finnes, kan alle i workspacet bruke den. Konfigurasjonen
lagres kryptert i workspacet. Jobber, pipelines og alarmer peker på destinasjonen med
ID-en dens, som du finner med `databricks notification-destinations list`. Se
[Slack-varsler](../guider/overvaake-og-drifte/slack-alarmer.md) for oppsettet.

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

## Relatert innhold

**Forklaringer:**

- [Overvåking](../om-plattformen/konsepter/overvaaking.md) — hvorfor varsling er teamets
  ansvar

**Guider:**

- [Slack-varsler](../guider/overvaake-og-drifte/slack-alarmer.md) — opprette en
  notification destination for Slack
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
