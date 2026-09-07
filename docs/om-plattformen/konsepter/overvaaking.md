---
title: Overvåking
description: Hvordan ansvaret for overvåking er delt mellom teamet og Dataspeilet, hvilket innsyn du får uten oppsett, og hvorfor varsling er noe teamet selv skrur på.
diataxis: explanation
---

# Overvåking

Denne siden forklarer hvordan ansvaret for overvåking er delt, hva du får ut av boksen, og
hvorfor varsling er konfigurasjon teamet selv legger i bundlen. De praktiske oppskriftene
står i guidene det lenkes til underveis.

## Du bygger det, du drifter det

Ansvaret for overvåking følger [eierskapet](eierskap-og-forvaltning.md). Dataspeilet eier
og overvåker plattformen: workspaces, kataloger, landing zones, nettverk og forbruket på
workspace-nivå. Teamet eier og overvåker det som kjører der: pipelines, jobber og dataene
de produserer. Teamet som bygger en pipeline drifter den også, med den tekniske eieren som
ansvarlig.

Dataspeilet ser ikke på innholdet i workspacene og kan ikke vite om en feilet kjøring
haster, om tallene i en tabell er plausible, eller om en fil som uteble fra kilden, er et
avvik. Den vurderingen krever kjennskap til dataene, og den sitter hos teamet.

Forbruket følger samme deling. Dataspeilet ser totalen per workspace og får varsel når den
passerer en terskel, men bare teamet vet hvilke jobber som står bak. Derfor tagger teamet
jobbene sine med team og prosess, se [Tagging av
kostnader](../../guider/overvaake-og-drifte/kostnadstagging.md).

## En feilet jobb varsler ingen

Som standard blir en feilet kjøring bare stående som rød i kjørehistorikken i Databricks
til noen ser etter. Skal teamet få beskjed, må varsling konfigureres. På plattformen
ligger den konfigurasjonen i [bundlen](databricks-bundles.md), sammen med jobben den
gjelder:

- **E-post ved feil** er den enkleste formen: feltet `email_notifications.on_failure` på
  jobben sender e-post til adressene som er listet der.

- **Slack-varsling** krever en *notification destination* i workspacet, et engangsoppsett
  som må gjøres av en workspace-admin. Deretter kan alle jobber i workspacet peke på
  den. Se [Slack-varsler](../../guider/overvaake-og-drifte/slack-alarmer.md).

At varslinga ligger i bundlen, betyr at den versjoneres, gjennomgås og deployes sammen med
jobben, og at den kan variere mellom miljøer: aktiv i prod, avslått i stage. Når varselet
kommer, se [Feilsøke med logger](../../guider/overvaake-og-drifte/logging.md) og
[Gjenopprette etter feil i
pipelines](../../guider/overvaake-og-drifte/gjenopprette-etter-feil.md).

## Innsynet du får uten oppsett

Noe innsyn følger med Databricks uten at teamet konfigurerer noe:

- **Kjørehistorikk.** Jobs & Pipelines i workspacet viser alle kjøringer med status,
  varighet og hvilken task som feilet. Historikken oppbevares i 60 dager.

- **Logger.** Hver kjøring har driver- og Spark-logger, og egne loggmeldinger fra
  notebooks havner samme sted. Hvordan du finner og tolker dem, står i [Feilsøke med
  logger](../../guider/overvaake-og-drifte/logging.md).

Dette innsynet er reaktivt: du må selv se etter. Skal du få beskjed, trenger du varsling.
Skal du fange feil i selve dataene, trenger du [kvalitetssjekker](datakvalitet.md).

## Grønn kjøring betyr ikke riktige data

Varsling ved feilede kjøringer fanger bare tekniske feil. En pipeline kan kjøre grønt og
likevel levere gale tall: kilden endret format, en kolonne ble stående tom, eller dagens
fil kom aldri. Å oppdage slikt er også teamets ansvar.

Mønsteret på plattformen er å la kvalitetssjekker bruke den samme varslingskjeden som
tekniske feil: en sjekk som avdekker ugyldige data, feiler jobben, og jobbens varsling
sier fra. I Declarative Pipelines gjør
[expectations](https://docs.databricks.com/aws/en/ldp/expectations) med `FAIL UPDATE`
dette. For tabeller utenfor Declarative Pipelines gjør [eksempelbundlen med
DQX](https://github.com/oslokommune/padda-databrikker/tree/main/bundles/datakvalitet_dqx)
det samme, se [Installere og bruke DQX](../../guider/overvaake-og-drifte/bruke-dqx.md).

For overvåking som ikke hører hjemme i en pipelinekjøring, finnes to verktøy til.
[Alerts](../../referanse/datakvalitet.md#alerts) er SQL-spørringer som kjører på tidsplan
og varsler når resultatet bryter en betingelse, for eksempel at data er eldre enn
forventet. Databricks har også innebygd
[dataprofilering](https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-quality-monitoring/data-profiling/),
tidligere kalt Lakehouse Monitoring, som teamet kan skru på for egne tabeller for å følge
statistikk og endringer i datafordelinga over tid.

## Relatert innhold

**Forklaringer:**

- [Eierskap og forvaltning](eierskap-og-forvaltning.md) — rollene bak ansvarsdelingen
- [Datakvalitet](datakvalitet.md) — hvorfor riktige data krever løpende oppmerksomhet
- [Declarative Automation Bundles](databricks-bundles.md) — hvorfor konfigurasjon bor i
  bundlen

**Guider:**

- [Slack-varsler](../../guider/overvaake-og-drifte/slack-alarmer.md)
- [Feilsøke med logger](../../guider/overvaake-og-drifte/logging.md)
- [Gjenopprette etter feil i pipelines](../../guider/overvaake-og-drifte/gjenopprette-etter-feil.md)
- [Installere og bruke DQX](../../guider/overvaake-og-drifte/bruke-dqx.md)
- [Tagging av kostnader](../../guider/overvaake-og-drifte/kostnadstagging.md)

**Referanser:**

- [Datakvalitet](../../referanse/datakvalitet.md) — constraints, expectations, alerts og
  DQX
