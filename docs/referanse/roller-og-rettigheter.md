---
title: Roller og rettigheter
description: Plattformens roller, rettigheter, ansvarsområder og tilgangsmodell.
diataxis: reference
icon: lucide/merge
---

# Roller og rettigheter

!!! info "Opprinnelse"
    Denne siden er sammenslått fra `docs/guides/roller/*.md` og `docs/notion/tilgangsstyring-og-roller.md`. Tutorial-delen (innlogging, SSO, flyt) ligger under [Slik får du tilgang](../kom-i-gang/slik-faar-du-tilgang.md).

Denne siden gir en samlet oversikt over rollene i dataplattformen, deres rettigheter og ansvarsområder.

## Roller

| Rolle | Unity Catalog-rettigheter | Ansvar |
|-------|--------------------------|--------|
| **Ansatt / datautforsker** | `USE_CATALOG` i felleskatalogen | Utforske data der eksplisitt tilgang er gitt |
| **Dataanalytiker** | `USE_CATALOG`, `USE SCHEMA`, `CREATE TABLE` | Analyse og prototyping |
| **Dataansvarlig (data owner)** | Schema Owner | Tilgang, datakvalitet og dokumentasjon i sitt domene |
| **Workspace-admin** | Catalog Owner | Workspace-ressurser og job-ACL-er |
| **Dataplattform-admin** | Account-nivå | Plattformdrift, SCIM, nettverk |

## Ansatt / datautforsker (grunnleggende tilgang)

Denne rollen har `USE_CATALOG` i felleskatalogen. Du kan lese data der du har fått eksplisitte rettigheter (f.eks. via gruppe/AD-gruppe), men du kan ikke opprette nye tabeller eller endre eksisterende.

## Dataanalytiker

Rollen har `USE_CATALOG`, `USE SCHEMA` og `CREATE TABLE`. Du kan lese, lage egne tabeller og prototyper, men endringer i produksjonsskjemaer må koordineres med dataeier.

## Dataansvarlig (data owner)

Rollen er ansvarlig for struktur, tilgang og datakvalitet i sitt domene.

### Løpende ansvar
- Forvalte tilgang og følge sikkerhetskrav (sensitivitet, persondata).
- Godkjenne nye tabeller og bryte ned eierskap til schema-nivå.
- Sikre dokumentasjon (datakatalog, README, feltbeskrivelser) og kontaktpunkt.
- Følge naming- og governance-prinsipper fra plattformteamet.

## Workspace-admin

Workspace-admin har Catalog Owner-rettigheter og administrerer workspace-ressurser, job-ACL-er og brukergrupper på workspace-nivå.

## Dataplattform-admin

Dataplattform-admin opererer på account-nivå og har ansvar for plattformdrift, SCIM-konfigurasjon, nettverksoppsett og administrasjon av workspaces.

## Grupper i Entra ID

Grupper defineres i Entra ID, og synkroniseres til Databricks som både workspace-grupper og Unity Catalog-grupper. Følgende grupper er de viktigste:

SYE, 5 roller, workspace admin, data analyst, dataprodukt utvikler, ansatt/browse

For Power BI er det behov for en servicebruker.

## Tilgangsstyring i Unity Catalog

Unity Catalog benytter RBAC. Følgende prinsipper gjelder:

- **Catalog Owner** tildeles Databricks-Workspace-admin
- **Schema Owner**: Databricks-Dataansvarlig får eierskap i sine schemas for å administrere tabeller og views.
- **Table/Volume Grants**: Analytikere får `SELECT`, mens skrive-rettigheter kun gis til pipelines.
- **Data Explorer**: `Ansatt-Browse` får `USE CATALOG/USE SCHEMA` + `SHOW TABLES` slik at metadata er synlig, men ikke data.

## Oversikt over tilgangsnivåer

- **Identiteter og grupper**: Alltid i Entra ID; Databricks leser dem via SCIM.
- **Account level access**: Styres av `Dataplattform-Utvikler-Account`. Her ligger informasjon om workspaces, SCIM-klienter og nettverk.
- **Workspace level access**: Ligger i Databricks workspace (Jobs, Repos). Git/Bundle beskriver hvilke grupper som skal ha hvilke rettigheter.
- **Unity Catalog / metadata**: Beskrives via grants i IaC og håndheves av UC. Alle brukere med `Ansatt-Browse` kan lese metadata, men ikke innhold.
- **Flyt**: Entra ID → SCIM → Databricks Account → Workspace → Unity Catalog. Når vi dokumenterer en ny tilgang bør vi alltid angi hvilket nivå (account, workspace, catalog/schema/table) som påvirkes.

## GitHub Actions service principal

Hvert team har en dedikert service-principal i Entra ID (f.eks. `spn-github-{team}`). Denne:

- har app-registrering med klienthemmelighet
- brukes av GitHub Actions-workflows til deploy (bundle deploy, uc grants, etc.)

På den måten opptrer CI/CD som en "vanlig" bruker.
