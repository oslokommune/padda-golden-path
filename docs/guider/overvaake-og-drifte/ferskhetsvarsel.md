---
title: Sette opp ferskhetsvarsel
description: Ta i bruk ferskhetsvarselet fra bundle-malen, slik at teamet får beskjed i Slack når en tabell ikke har fått nye data innenfor ferskhetsgrensen.
diataxis: how-to
---

# Sette opp ferskhetsvarsel

Denne guiden viser hvordan du tar i bruk ferskhetsvarselet i en bundle som er generert med
`include_freshness_alert: yes`. Ferskhetsvarselet er en jobb som feiler når en overvåket
tabell ikke har fått nye data innenfor ferskhetsgrensen sin, og feilen sendes til Slack.
Når du er ferdig, kjører jobben hver morgen i prod og sier fra om tabeller med for gamle
data.

Har teamet en eldre bundle, finnes valget `include_freshness_alert` når dere genererer en
ny bundle fra malen.

## Før du begynner

Sørg for at du har:

- En bundle generert med `include_freshness_alert: yes`. Se [Ta i bruk
  bundles](../utvikle-og-deploye/ta-i-bruk-bundles.md).
- En notification destination av typen **Slack** i både stage- og prod-workspacet, og
  ID-ene til dem. Se trinn 1 og 2 i [Sette opp Slack-varsler](slack-varsler.md).
- Tabeller å overvåke, med en kolonne med innlastingstidspunkt av typen `TIMESTAMP`.
  Mangler tabellen en slik kolonne, se [Legge til en kolonne med
  innlastingstidspunkt](#legge-til-en-kolonne-med-innlastingstidspunkt).

## Trinn 1: Sett ID-en til Slack-destinasjonen

Åpne `databricks.yml` og bytt ut `REPLACE_WITH_DESTINATION_ID` med ID-en til
destinasjonen i hvert target:

```yaml
targets:
  stage:
    # ...
    variables:
      # ...
      slack_destination_id: <ID fra stage-workspacet>

  prod:
    # ...
    variables:
      # ...
      slack_destination_id: <ID fra prod-workspacet>
```

Andre jobber i bundlen kan bruke den samme variabelen, se trinn 3 i [Sette opp
Slack-varsler](slack-varsler.md#trinn-3-pek-jobben-pa-destinasjonen-i-bundlen).

## Trinn 2: List tabellene som skal overvåkes

Åpne `resources/freshness_alert.job.yml`. Hver overvåket tabell er én linje under
`parameters`, med fullt tabellnavn, kolonne med innlastingstidspunkt og ferskhetsgrense,
skilt av mellomrom:

```yaml
            parameters:
              - ${var.catalog}.${var.schema}.bronze_nyctaxi load_date 26h
```

Bytt ut eksempeltabellen, eller `TODO_table` hvis bundlen ble generert uten
eksempeljobbene, med tabellene dine. Legg til én linje per tabell.

Sett ferskhetsgrensen til hvor ofte tabellen skal få nye data, pluss en margin. En tabell
som lastes inn én gang i døgnet, kan for eksempel ha `26h`. Grensen skrives som et
positivt heltall fulgt av `m`, `h` eller `d`. Formatet er beskrevet i [Varsling og
alarmer](../../referanse/varsling-og-alarmer.md#overvakede-tabeller).

## Trinn 3: Juster tidsplanen ved behov

Jobben kjører hver dag kl. 07:00 norsk tid. Skal tabellene sjekkes oftere eller på et
annet tidspunkt, endrer du cron-uttrykket i samme fil:

```yaml
      schedule:
        quartz_cron_expression: "0 0 7 * * ?"
        timezone_id: Europe/Oslo
        pause_status: UNPAUSED
```

Hver kjøring som finner et problem, sender ett varsel. Sjekker du oftere, får du derfor
flere varsler til problemet er løst.

## Trinn 4: Deploy til stage og test

I stage står tidsplanen på pause, så der kjører du jobben selv. Testen under bruker
eksempeltabellen `bronze_nyctaxi`. Overvåker du andre tabeller, kjører du jobbene som
fyller dem i stedet for eksempelpipelinen.

1. Deploy bundlen og kjør ferskhetsvarselet før eksempelpipelinen har kjørt:

    ```bash
    databricks bundle deploy -t stage -p MY_TEAM_STAGE
    databricks bundle run -t stage -p MY_TEAM_STAGE freshness_alert
    ```

    Kjøringen feiler fordi tabellen ikke finnes ennå, og det kommer en melding i
    Slack-kanalen. Meldingen sier bare at jobben feilet. Hvilke tabeller som har
    problemer, står i kjøreresultatet (*run output*) til kjøringen i workspacet:

    ```text
    FreshnessAlertError: Freshness alert: 1 of 1 watched tables are stale or could not be checked.

    Could not check (wrong table or column name, column not TIMESTAMP, or missing SELECT permission):
    - <katalog>.default.bronze_nyctaxi: [TABLE_OR_VIEW_NOT_FOUND] The table or view ...
    ```

    Har eksempelpipelinen allerede kjørt i stage, går denne kjøringen grønt i stedet.
    Gå da videre til punkt 3.

2. Kjør eksempelpipelinen, slik at tabellen får data:

    ```bash
    databricks bundle run -t stage -p MY_TEAM_STAGE example_pipeline_job
    ```

3. Kjør ferskhetsvarselet på nytt:

    ```bash
    databricks bundle run -t stage -p MY_TEAM_STAGE freshness_alert
    ```

## Trinn 5: Deploy til prod

Deploy bundlen til prod slik teamet vanligvis gjør, se [Deploye til produksjon med GitHub
Actions](../utvikle-og-deploye/deploye-til-produksjon.md). I prod er tidsplanen aktiv, og
jobben kjører som service principalen i `run_as`.

## Bekreft resultatet

- Den siste kjøringen i stage fra trinn 4 er grønn. Loggen har én INFO-linje per
  overvåket tabell, for eksempel:

    ```text
    INFO:<pakke>.freshness.tasks:fresh: <katalog>.default.bronze_nyctaxi: latest load timestamp 2026-10-21 13:02 UTC, age 7m, threshold 26h
    ```

- I prod-workspacet ligger jobben `freshness_alert` under **Jobs & Pipelines** med en
  aktiv tidsplan, og destinasjonen står oppført for **Failure** under **Job
  notifications**.

## Feilsøking

??? failure "Feilmelding ved deploy: `Invalid webhook id 'REPLACE_WITH_DESTINATION_ID'`"

    `slack_destination_id` har fortsatt plassholderen i targeten du deployer til:

    ```text
    Error: cannot create resources.jobs.freshness_alert: Invalid webhook id 'REPLACE_WITH_DESTINATION_ID' in on_failure. Webhook IDs must be valid UUIDs. (400 INVALID_PARAMETER_VALUE)
    ```

    `databricks bundle validate` godtar plassholderen, så feilen kommer først ved deploy.
    Andre ressurser i bundlen kan være deployet før feilen. Sett ID-en som i trinn 1, og
    deploy på nytt.

??? failure "Tabellen står under `Could not check`"

    Jobben fikk ikke lest det nyeste innlastingstidspunktet. Årsaken står etter
    tabellnavnet i kjøreresultatet:

    - Tabellen eller kolonnen finnes ikke. Sjekk stavemåten, og at tabellen finnes i
      katalogen og skjemaet targeten bruker.
    - Kolonnen har ikke typen `TIMESTAMP`. `DATE` og `TIMESTAMP_NTZ` støttes ikke.
    - Identiteten jobben kjører som, mangler lesetilgang til tabellen. I prod er det
      service principalen i `run_as`.

??? failure "Ingen melding i Slack når jobben feiler"

    Sjekk at destinasjonen er av typen Slack. `databricks notification-destinations list`
    viser typen i `destination_type`, som skal være `SLACK`. En destinasjon av typen
    Webhook poster et format Slack ikke viser som melding. Se også feilsøkingen i [Sette
    opp Slack-varsler](slack-varsler.md).

??? failure "Ikke noe varsel, selv om kilden ikke har levert nye data"

    En full refresh av tabellen skriver innlastingstidspunktet på nytt for alle rader,
    også når kilden ikke har nye data. Da ser tabellen fersk ut, og varselet går ikke
    før ferskhetsgrensen er passert på nytt.

## Legge til en kolonne med innlastingstidspunkt

I Declarative Pipelines legger du kolonnen til der dataene leses inn, slik
eksempelpipelinen i bundle-malen gjør:

```python
return (
    spark.readStream.format("delta")
    .load(autoloader_path)
    .withColumn("load_date", F.current_timestamp())
    .select("*", "_metadata")
)
```

Tabeller som leser fra denne tabellen, får med kolonnen så lenge de tar den med i
utvalget, slik `bronze_nyctaxi` gjør. For en vanlig Delta-tabell legger du til kolonnen
på samme måte i DataFrame-en før du skriver den.

Ikke bruk tidspunktet hendelsen skjedde i kilden. Kommer det sene hendelser, ser en tabell
som nettopp fikk nye data, for gammel ut.

## Relatert innhold

**Guider:**

- [Sette opp Slack-varsler](slack-varsler.md) — notification destination for Slack
- [Feilsøke med logger](logging.md) — finne kjøreresultatet til en kjøring

**Forklaringer og referanser:**

- [Overvåking](../../om-plattformen/konsepter/overvaaking.md) — hvorfor
  ferskhetsvarselet måler tabellen, ikke kjøringen
- [Varsling og alarmer](../../referanse/varsling-og-alarmer.md#ferskhetsvarsel) — valget,
  jobben, formatet og utfallene
