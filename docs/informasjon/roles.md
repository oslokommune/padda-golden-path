# Tilgangsstyring og roller
Denne siden beskriver de viktigste byggeklossene for tilgangsstyring i dataplattformen. Vi bruker Entra ID som master for identiteter og roller, Databricks (account/workspace) for kjøring av kode og Unity Catalog for dataautorisasjon. 

## Flytskjema
Teknisk flyt:

1. **Entra ID** forvalter brukere, sikkerhetsgrupper og service-principals.
2. Grupper synkroniseres til Databricks via SCIM.
3. Ved pålogging bruker vi **SSO (SAML/SCIM)** slik at brukeren autentiseres en gang og får token i både konto og arbeidsområde.
4. Databricks workspace mapper gruppene til Unity Catalog-roller og til workspace-/job-ACL-er.
5. Unity Catalog kontrollerer sluttbrukerens tilgang til databaser, tabeller, volum og katalogmetadata.

## SSO
Databricks er konfigurert med Entra ID som Identity Provider. Brukere:

- logger på via SAML/SCIM SSO uten egne Databricks-passord
- får automatisk MFA-policy fra Entra ID
- opplever sømløs bytte mellom Workspaces fordi token kommer fra samme SSO

## Grupper
Grupper defineres i Entra ID, og synkroniseres til Databricks som både workspace-grupper og Unity Catalog-grupper. Følgende grupper er de viktigste:

TODO!!!
| Gruppe | Hovedtilgang | Typisk bruker |
| --- | --- | --- |
| `Dataplattform-Utvikler-Account` | Admin-tilgang på Databricks Account-nivå (opprette workspaces, konfigurere SCIM) | Plattform-team |
| `Dataplattform-Utvikler-Workspace` | CAN_MANAGE på delt Dev-workspace og job cluster | Plattform-utviklere |
| `Dataanalyst-Python` | CAN_RUN på notebooks/jobs og SELECT i relevante kataloger | Analytikere / Data Scientists |
| `Dataprodusent-Utvikler` | Eierskap til egne Catalog/Schemas i Unity Catalog, samt jobbplaner | Team som publiserer datasett |
| `Ansatt-Browse` | Lesetilgang til metadata i Unity Catalog, ingen runtime-tilgang | Forretningsbrukere |


## Hvordan gjøres tilgangsstyring i Unity Catalog
Unity Catalog benytter RBAC. Vi bruker følgende prinsipper:

- **Catalog Owner** tildeles kun til plattformteam; team får `USE CATALOG`.
- **Schema Owner**: Dataprodusent-team får eierskap i sine schemas for å administrere tabeller og views.
- **Table/Volume Grants**: Analytikere får `SELECT`, mens skrive-rettigheter kun gis til pipelines.
- **Data Explorer**: `Ansatt-Browse` får `USE CATALOG/USE SCHEMA` + `SHOW TABLES` slik at metadata er synlig, men ikke data.

TODO: Alle grants lagres i Git via IaC slik at revisjon er enkel.


## Github-actions-bruker for team
TODO:
Hvert team har en dedikert service-principal i Entra ID (f.eks. `spn-github-{team}`). Denne:

- har app-registrering med klienthemmelighet
- brukes av GitHub Actions-workflows til deploy (bundle deploy, uc grants, etc.)

På den måten opptrer CI/CD som en “vanlig” bruker.

## Oversikt over informasjon og tilgangstyper
- **Identiteter og grupper**: Alltid i Entra ID; Databricks leser dem via SCIM.
- **Account level access**: Styres av `Dataplattform-Utvikler-Account`. Her ligger informasjon om workspaces, SCIM-klienter og nettverk.
- **Workspace level access**: Ligger i Databricks workspace (Jobs, Repos). Git/Bundle beskriver hvilke grupper som skal ha hvilke rettigheter.
- **Unity Catalog / metadata**: Beskrives via grants i IaC og håndheves av UC. Alle brukere med `Ansatt-Browse` kan lese metadata, men ikke innhold.
- **Flyt**: Entra ID → SCIM → Databricks Account → Workspace → Unity Catalog. Når vi dokumenterer en ny tilgang bør vi alltid angi hvilket nivå (account, workspace, catalog/schema/table) som påvirkes.
