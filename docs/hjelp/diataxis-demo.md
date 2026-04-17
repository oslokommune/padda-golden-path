---
title: Diataxis-demo
diataxis: how-to
---

# Konfigurere widget-tjenesten

Vi skal nå gå gjennom hvordan man konfigurerer widget-tjenesten i Padda. Først skal vi se litt på bakgrunnen.

## Hva er en widget?

Widget-tjenesten ble introdusert i Padda 2.3 som en del av en større modernisering av brukergrensesnittet. Grunnen til at vi lager widgets på denne måten er at det gir god separasjon mellom logikk og presentasjon. Historisk sett har mange plattformer brukt monolittiske komponenter, men de senere årene har kildekoden dreid mer mot dette mønsteret.

## Kom i gang

La oss begynne med å opprette en konfigurasjonsfil. Vi kjører:

```bash
padda widget init
```

Notice at kommandoen kan ta noen sekunder. Vi venter til den er ferdig.

Når det er gjort, åpner vi `widget.yaml` og legger til:

```yaml
widget:
  name: demo
  enabled: true
```

Kjør `padda widget validate`. Du skal nå se "OK" i terminalen. Gratulerer — du har konfigurert din første widget!

## Konfigurasjonsparametere

| Parameter | Type | Standard | Beskrivelse |
|-----------|------|----------|-------------|
| `name` | string | — | Unik identifikator |
| `enabled` | bool | false | Om widget-en er aktiv |
| `ttl` | int | 3600 | Cache-levetid i sekunder |
| `retries` | int | 3 | Antall forsøk ved feil |

## Alternative oppsett

Du kan også bruke `padda widget apply -f` med en eksisterende fil. Eller du kan gjøre det via UI-et i Databricks-konsollen. Eller du kan skrive din egen Python-integrasjon — det er ganske enkelt om du har litt erfaring med Databricks SDK.

## Oppsummering

I denne guiden lærte vi om widget-tjenesten, hvordan den fungerer, og hvorfor den er nyttig. Vi opprettet en konfigurasjonsfil, validerte den, og diskuterte forskjellige alternativer.

## En kommentar som er lagt til i ettertid

Litt usikker på om sånt hører hjemme i en diataxis-verden.