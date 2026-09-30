---
title: Sette opp Slack-varsler
description: Opprett en notification destination for en Slack-kanal, og la jobbene i bundlen varsle der når de feiler.
diataxis: how-to
---

# Sette opp Slack-varsler

Denne guiden viser hvordan du kan få varsler i Slack når en jobb feiler. Først lager du
en webhook for kanalen i Slack, deretter oppretter du en *notification destination* i
workspacet, et objekt som lagrer URL-en til webhooken. Det er et engangsoppsett per
workspace, og det må gjøres av en workspace-admin. Til slutt peker du på destinasjonen fra
jobben i [bundlen](../../om-plattformen/konsepter/databricks-bundles.md), og det kan alle
som deployer bundlen gjøre.

## Før du begynner

Sørg for at du har:

- En bundle med en jobb, se [Ta i bruk bundles](../utvikle-og-deploye/ta-i-bruk-bundles.md).
- En Slack-kanal teamet følger med på.
- En workspace-admin på teamet til trinn 2, enten deg selv eller noen som kan gjøre det
  for deg. Se [Roller og rettigheter](../../referanse/roller-og-rettigheter.md#workspace-admin).

## Trinn 1: Lag en webhook i Slack

1. Gå til [api.slack.com/apps](https://api.slack.com/apps) og opprett en ny app i Oslo
   kommunes Slack-workspace. Gi den et beskrivende navn.
2. Åpne **Incoming Webhooks** i menyen til appen og skru på **Activate Incoming
   Webhooks**.
3. Klikk **Add New Webhook to Workspace**, velg kanalen varslene skal gå til, og klikk
   **Authorize**.
4. Kopier URL-en under **Webhook URLs for Your Workspace**. Den begynner med
   `https://hooks.slack.com/services/`.

I stage står tidsplanene på pause, så der varsler jobben bare når noen kjører den selv.
Vil du ha disse meldingene i en annen kanal enn prod, legger du til en egen webhook for
stage i samme app.

!!! warning "URL-en til webhooken er en hemmelighet"

    Den som har URL-en, kan poste i kanalen. Ikke legg den i git eller i bundlen. Slack
    trekker tilbake URL-er som lekker ut, for eksempel til et offentlig repo.

## Trinn 2: Opprett en notification destination i workspacet

1. Klikk brukernavnet ditt øverst til høyre i workspacet og velg **Settings**.
2. Under **Workspace admin**, åpne fanen **Notifications** og klikk **Manage**.
3. Klikk **Add destination**, velg **Slack** som type, gi destinasjonen et navn, lim inn
   URL-en fra trinn 1, og klikk **Create**.

Databricks lagrer URL-en kryptert. Alle i workspacet kan bruke destinasjonen når den er
opprettet.

Du trenger ID-en til destinasjonen i trinn 3. Finn den ved å liste destinasjonene i
workspacet:

```bash
databricks notification-destinations list -p MY_TEAM_STAGE
```

Gjenta trinnet for prod-workspacet. ID-en er forskjellig i hvert workspace.

## Trinn 3: Pek jobben på destinasjonen i bundlen

Legg til en variabel i `databricks.yml`, og sett ID-en for hvert target:

```yaml
variables:
  slack_destination_id:
    description: Notification destination for Slack-varsler

targets:
  stage:
    # ...
    variables:
      slack_destination_id: <ID fra stage-workspacet>

  prod:
    # ...
    variables:
      slack_destination_id: <ID fra prod-workspacet>
```

Legg så til `webhook_notifications` på jobben i `resources/*.job.yml`:

```yaml
resources:
  jobs:
    paddeobservasjoner_job:
      name: paddeobservasjoner_job
      # ...
      webhook_notifications:
        on_success: # Midlertidig, fjernes i trinn 4
          - id: ${var.slack_destination_id}
        on_failure:
          - id: ${var.slack_destination_id}
      notification_settings:
        no_alert_for_skipped_runs: true
```

`webhook_notifications` er feltet for alle notification destinations, også Slack. De andre
hendelsene du kan varsle på, og hva `no_alert_for_skipped_runs` gjør, står i [Varsling og
alarmer](../../referanse/varsling-og-alarmer.md#varsler-pa-jobber).

## Trinn 4: Deploy og test

Deploy bundlen til stage og kjør jobben:

```bash
databricks bundle validate -t stage -p MY_TEAM_STAGE
databricks bundle deploy -t stage -p MY_TEAM_STAGE
databricks bundle run -t stage -p MY_TEAM_STAGE paddeobservasjoner_job
```

Når kjøringen er ferdig, skal meldingen dukke opp i kanalen. Fjern så `on_success` fra
jobben og deploy på nytt:

```bash
databricks bundle deploy -t stage -p MY_TEAM_STAGE
```

## Bekreft resultatet

Åpne jobben under **Jobs & Pipelines** i workspacet. I stage heter den `[dev <brukernavn>]
paddeobservasjoner_job`. I panelet **Job details**, under **Job notifications**, skal
destinasjonen stå oppført for **Failure**.

## Feilsøking

??? failure "Ingen melding i Slack når jobben feiler"

    - Sjekk at ID-en i targeten hører til samme workspace som jobben kjører i.
    - Kjøringen kan ha blitt hoppet over i stedet for å feile. Slike kjøringer varsles
      ikke når `no_alert_for_skipped_runs` er satt.
    - Feiler en task og prøver på nytt, kommer jobbvarselet først når hele kjøringen har
      feilet.
    - Webhooken kan være trukket tilbake fordi URL-en har lekket ut. Lag en ny webhook i
      Slack og oppdater destinasjonen.
    - Kanalen kan være arkivert. Da avviser Slack meldingene.

??? failure "Pipelinen feiler, men det kommer ikke noe varsel"

    En pipeline kan bare varsle på e-post. Kjører den på egen tidsplan, utenom jobben, får
    du derfor ikke noe Slack-varsel. Legg pipelinen inn som en task i jobben, se [Skrive
    transformasjoner](../bearbeide-data/skrive-transformasjoner.md#trinn-4-legg-transformasjonen-inn-i-innlastingsjobben).
    Da feiler jobben når pipelinen feiler, og jobbvarselet sendes.

??? failure "Finner ikke fanen Notifications under Settings"

    Fanen vises bare for workspace-admins. Be en workspace-admin på teamet om å gjøre
    trinn 2.

## Relatert innhold

**Guider:**

- [Feilsøke med logger](logging.md)
- [Gjenopprette etter feil i pipelines](gjenopprette-etter-feil.md)

**Forklaringer og referanser:**

- [Overvåking](../../om-plattformen/konsepter/overvaaking.md)
- [Varsling og alarmer](../../referanse/varsling-og-alarmer.md)
- [Roller og rettigheter](../../referanse/roller-og-rettigheter.md#workspace-admin)

**Ekstern dokumentasjon:**

- [Manage notification destinations](https://docs.databricks.com/aws/en/admin/workspace-settings/notification-destinations)
- [Add notifications on a job](https://docs.databricks.com/aws/en/jobs/notifications)
- [Sending messages using incoming webhooks](https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks)
