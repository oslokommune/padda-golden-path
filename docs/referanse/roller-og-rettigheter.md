---
title: Roller og rettigheter
description: Plattformens roller, rettigheter, ansvarsområder og tilgangsmodell.
diataxis: reference
---

# Roller og rettigheter

Denne siden gir en oversikt over rollene (gruppene) og tilgangene på
plattformen. For *hvorfor* plattformen bruker rollebasert tilgangsstyring, se
konseptsiden [Roller og
tilgangsstyring](../om-plattformen/konsepter/roller-og-tilgangsstyring.md).

## Grupper

Hvert workspace har tre faste grupper — én for hver av rollene workspace-admin,
dataanalytiker og dataansvarlig. I tillegg finnes to plattformovergripende
grupper som foreløpig bare er opprettet for DIG. Det er gruppen du er medlem av
som avgjør hva du kan gjøre. Medlemskap forvaltes gjennom Entra ID — se [Slik
får du tilgang](../kom-i-gang/slik-faar-du-tilgang.md).

!!! note "Under arbeid"
    Entra-gruppene er foreløpig ikke opprettet for alle workspaces. Dette er
    under utrulling, så oppsettet kan se annerledes ut for ditt workspace enn det
    som er beskrevet her. Ta kontakt med plattformteamet hvis du er usikker på
    hva som gjelder for deg.

Alle gruppene følger samme mønster med `DS-`-prefiks og organisasjonskode, der
`{ORG}` byttes ut med organisasjonskoden din.

De tre faste gruppene per workspace er:

| Gruppe                      | Rolle                               |
|-----------------------------|-------------------------------------|
| `DS-{ORG}_WORKSPACE_ADMINS` | Administratorer for ett workspace   |
| `DS-{ORG}_DATAANALYTIKERE`  | Analyse og prototyping i workspacet |
| `DS-{ORG}_DATAANSVARLIGE`   | Dataansvarlige i sitt domene        |

De to plattformovergripende gruppene, som foreløpig bare finnes for DIG:

| Gruppe                        | Rolle                                      |
|-------------------------------|--------------------------------------------|
| `DS-DIG_DATAPLATTFORM_ADMINS` | Plattformforvaltere på tvers av workspaces |
| `DS-DIG_KATALOGBRUKERE`       | Lesetilgang til katalogmetadata            |

### Workspace-admin

Workspace-admin har Catalog Owner-rettigheter og administrerer
workspace-ressurser, Access Control Lists (ACL-er) for jobber og brukergrupper
på workspace-nivå. Deler teamet data med OpenSharing, har gruppa i tillegg
`CREATE SHARE` og `USE RECIPIENT` på metastoren, se [Dele data med en annen
Databricks-konto](../guider/dele-og-hente-ut/dele-med-annen-databricks-konto.md).

### Dataanalytiker

Rollen har `USE_CATALOG`, `USE SCHEMA` og `CREATE TABLE`, og kan lese data og
lage egne tabeller og prototyper. Den har ikke skrivetilgang til
produksjonsskjemaer.

### Dataansvarlig

Rollen er ansvarlig for struktur, tilgang og datakvalitet i sitt domene.

Løpende ansvar:

- Forvalte tilgang og følge sikkerhetskrav (sensitivitet, persondata).
- Godkjenne nye tabeller og bryte ned eierskap til schema-nivå.
- Sikre dokumentasjon (datakatalog, README, feltbeskrivelser) og kontaktpunkt.
- Følge navngivnings- og forvaltningsprinsipper fra plattformteamet.

### Dataplattform-admin

Dataplattform-admin opererer på kontonivå og har ansvar for plattformdrift,
konfigurasjon av SCIM (System for Cross-domain Identity Management),
nettverksoppsett og administrasjon av workspaces.

### Katalogbruker

Rollen har lesetilgang til katalogmetadata: den kan se hvilke kataloger,
schemaer og tabeller som finnes, men ikke innholdet i dem. Tilgang til selve
dataene gis eksplisitt per katalog eller schema.

## Tilgangsstyring i Unity Catalog

Unity Catalog benytter rollebasert tilgangskontroll (RBAC). Følgende prinsipper
gjelder:

- **Catalog Owner**: Tildeles workspace-admin.
- **Schema Owner**: Dataansvarlig får eierskap i sine schemaer for å
  administrere tabeller og views.
- **Table/Volume Grants**: Analytikere får `SELECT`, mens skrive-rettigheter kun
  gis til pipelines.
- **Data Explorer**: `KATALOGBRUKERE` får `USE CATALOG/USE SCHEMA` + `SHOW
  TABLES` slik at metadata er synlig, men ikke data.

### Modeller i Unity Catalog

Registrerte modeller styres med de samme mekanismene som tabeller. Den som
deployer en ML-bundle blir eier av skjemaet og modellen; bundlen gir
konsumentgruppen rettighetene den trenger.

| Handling | Privilegium | Gis av |
|----------|-------------|--------|
| Opprette skjema for modellen | `USE CATALOG`, `CREATE SCHEMA` på katalogen | Katalogeier eller `padda-iac` |
| Registrere nye versjoner | Eierskap til modellen, eller `CREATE MODEL` på skjemaet | Deploy av bundlen |
| Bruke modellen til inferens | `USE CATALOG`, `USE SCHEMA`, `EXECUTE` på modellen | `grants` på modellressursen i bundlen |
| Lese prediksjoner | `USE CATALOG`, `USE SCHEMA`, `SELECT` | `grants` på skjemaressursen i bundlen |
| Kalle et serving-endepunkt | `CAN_QUERY` på endepunktet | `permissions` på endepunktressursen |

Se [MLflow og modellregister](mlflow-og-modellregister.md#privilegier).

## Oversikt over tilgangsnivåer

- **Identiteter og grupper**: Alltid i Entra ID; Databricks leser dem via SCIM.
- **Tilgang på kontonivå**: Styres av `Dataplattform-Utvikler-Account`. Her
  ligger informasjon om workspaces, SCIM-klienter og nettverk.
- **Tilgang på workspace-nivå**: Ligger i Databricks-workspacet (Jobs,
  Repos). Git/Bundle beskriver hvilke grupper som skal ha hvilke rettigheter.
- **Unity Catalog / metadata**: Beskrives via grants i infrastruktur som kode
  (IaC) og håndheves av Unity Catalog. Alle brukere med `KATALOGBRUKERE` kan
  lese metadata, men ikke innhold.
- **Flyt**: Entra ID → SCIM → Databricks Account → Workspace → Unity Catalog.

## GitHub Actions service principals

Deploy fra GitHub Actions skjer med egne service principals i Databricks, ikke
med personlige brukere. Hvert workspace har to:

- `{workspace}-gha-prs` med `USER`-tilgang, som validerer endringer på pull
  requests
- `{workspace}-gha-deploy` med `ADMIN`-tilgang, som deployer til workspacet
  (bundle deploy, Unity Catalog-grants, etc.)

Begge autentiserer med GitHub-føderasjon basert på OIDC, uten lagrede
klienthemmeligheter. På den måten opptrer CI/CD som en "vanlig" bruker.
