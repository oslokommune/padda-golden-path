---
title: Merke kostnader
description: Hvordan merke Databricks-jobber og -klynger med kostnadstaggene CostTeam og CostProcess for kostnadsfordeling på tvers av team og prosesser.
diataxis: how-to
---

# Merke kostnader

Denne veiledningen viser deg hvordan du merker ressursene i bundlene dine med kostnadstagger, slik at forbruket kan fordeles på riktig team og prosess i kostnadsrapportene.

## Før du begynner

Sørg for at du har:

- En bundle med en eller flere jobber du eier
- En klyngedefinisjon (`new_cluster`) i jobben din
- Avklart hvilket team og hvilken prosesstype ressursen tilhører

## De to godkjente taggene

Golden Path bruker to tagger for kostnadsfordeling:

- **`CostTeam`** — teamet som eier ressursen og som forbruket skal belastes.
- **`CostProcess`** — typen prosess ressursen utfører.

`CostProcess` skal ha én av følgende verdier:

| Verdi | Beskrivelse |
|-----------|-------------|
| `General` | Generelt forbruk som ikke passer i de andre kategoriene |
| `Ingest` | Innhenting av data inn på plattformen |
| `Transform` | Bearbeiding og transformasjon av data |
| `Query` | Spørringer og analyse |
| `Serve` | Servering av data til konsumenter |

## Hva som merkes automatisk

Plattforminfrastrukturen merkes automatisk av Golden Path, og du trenger ikke å gjøre noe for disse:

- AWS-ressurser provisjonert via infrastruktur-as-code.
- Databricks-compute som styres gjennom klyngepolicyer og landingssonen.

## Trinn 1: Legg til `custom_tags` på klyngen

Som bundle-forfatter setter du `CostTeam` og `CostProcess` som `custom_tags` på `new_cluster`-definisjonene dine. Eksempelet nedenfor er hentet fra `vscode-demo`-bundlen, der jobbklyngen kjører transformasjoner:

```yaml
      job_clusters:
        - job_cluster_key: job_cluster
          new_cluster:
            spark_version: 17.3.x-scala2.13
            node_type_id: i3.xlarge
            data_security_mode: SINGLE_USER
            custom_tags:
              CostTeam: padda
              CostProcess: Transform
            autoscale:
              min_workers: 1
              max_workers: 2
```

## Bekreft resultatet

Valider bundlen for å bekrefte at taggene er på plass:

```sh
databricks bundle validate
```

Den rendrede jobbklyngen skal nå vise `custom_tags` med `CostTeam` og `CostProcess`.

## Relatert innhold

- [Slack-alarmer](slack-alarmer.md)
- [Gjenopprette etter feil](gjenopprette-etter-feil.md)
