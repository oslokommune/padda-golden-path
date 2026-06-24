---
title: Tagging av kostnader
description: Hvordan tagge Databricks-jobber og -klynger med kostnadstaggene CostTeam og CostProcess for kostnadsfordeling på tvers av team og prosesser.
diataxis: how-to
---

# Tagging av kostnader

Denne veiledningen viser deg hvordan du merker jobbene dine med kostnadstaggene `CostTeam` og `CostProcess`, slik at forbruket fordeles på riktig team og prosess i kostnadsrapportene. Plattform-infrastruktur (AWS-ressurser og Databricks-compute via klyngepolicyer og landingssonen) tagges automatisk av Golden Path; denne veiledningen viser hvordan du merker dine egne jobber.

## Før du begynner

Sørg for at du har:

- En bundle med en eller flere jobber du eier
- Avklart hvilket team (`CostTeam`) ressursen tilhører
- Avklart hvilken prosesstype (`CostProcess`) jobben utfører

## Trinn 1: Merk en jobb med egen klynge (`new_cluster`)

Når jobben definerer sin egen klynge, setter du `CostTeam` og `CostProcess` som `custom_tags` på `new_cluster`. Eksempelet nedenfor er hentet fra `vscode-demo`-bundlen, der jobbklyngen kjører transformasjoner:

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

Velg `CostProcess` ut fra hva jobben gjør:

| Verdi | Brukes til |
|-----------|------------|
| `General` | Generelt forbruk som ikke passer i de andre kategoriene |
| `Ingest` | Innhenting av data inn på plattformen |
| `Transform` | Bearbeiding og transformasjon av data |
| `Query` | Spørringer og analyse |
| `Serve` | Servering av data til konsumenter |

## Trinn 2: Merk en jobb som bruker `existing_cluster_id`

Når jobben kjører på en eksisterende klynge du ikke eier, kan du ikke sette `custom_tags` på klyngen. Bruk i stedet job-nivå `tags` som søsken av `name` og `tasks`. Eksempelet nedenfor er hentet fra `excel_ingest`-bundlen:

```yaml
  jobs:
    ingest_excel_job:
      name: "Ingest Excel"
      timeout_seconds: 3600
      max_concurrent_runs: 1
      tags:
        CostTeam: padda
        CostProcess: Ingest
      tasks:
        - task_key: ingest_excel_task
          existing_cluster_id: ${var.existing_cluster_id}
```

Job-nivå `tags` er fallback når du ikke eier klyngen og dermed ikke kan sette `custom_tags` på den. Bruk samme `CostProcess`-verdier som i trinn 1.

## Bekreft resultatet

Valider bundlen for å bekrefte at taggene er på plass:

```sh
databricks bundle validate
```

Den rendrede jobben skal nå vise `custom_tags` på klyngen (trinn 1) eller `tags` på jobben (trinn 2) med `CostTeam` og `CostProcess`.

## Relatert innhold

- [Slack-alarmer](slack-alarmer.md)
- [Gjenopprette etter feil](gjenopprette-etter-feil.md)
