---
title: Koble Power BI til Databricks
description: Hvordan koble Power BI Desktop til SQL Warehouse for å utforske data og bygge rapporter.
diataxis: how-to
---

# Hvordan koble Power BI til Databricks

Denne guiden viser hvordan du kobler Power BI Desktop til et SQL Warehouse i Databricks,
slik at du kan utforske data og bygge rapporter mot tabellene i Unity Catalog.

## Før du begynner

Sjekk at:

- Du har tilgang til et Databricks-workspace med et SQL Warehouse (se
  [SQL Warehouse](../../referanse/sql-warehouse.md))
- Du har [Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop) installert

## Trinn 1 — Finn tilkoblingsdetaljer

Du trenger **Server hostname** og **HTTP path** fra SQL Warehouse:

1. Åpne Databricks-workspacet
2. Gå til **SQL Warehouses** i venstremenyen
3. Klikk på warehouset du vil bruke
4. Gå til fanen **Connection details**
5. Kopier **Server hostname** og **HTTP path**

Se [SQL Warehouse](../../referanse/sql-warehouse.md#tilkoblingsdetaljer) for hva de
ulike tilkoblingsdetaljene brukes til.

## Trinn 2 — Koble til fra Power BI Desktop

1. Åpne Power BI Desktop
2. Klikk **Get Data** → **More...**
3. Søk etter **Databricks** og velg konnektoren **Databricks** (ikke **Azure Databricks**
   — plattformen vår kjører på AWS, og OAuth-pålogging der støttes bare av
   **Databricks**-konnektoren)
4. Fyll inn:
    - **Server hostname**: verdien fra Trinn 1
    - **HTTP path**: verdien fra Trinn 1
5. Velg tilkoblingsmodus under **Data Connectivity mode** (se
   [DirectQuery vs. Import](#directquery-vs-import) nedenfor)
6. Klikk **OK**

### DirectQuery vs. Import

| Modus           | Passer når                                               | Fordeler                                   | Ulemper                                                                        |
|-----------------|----------------------------------------------------------|--------------------------------------------|--------------------------------------------------------------------------------|
| **Import**      | Rapporten skal være rask og dataene oppdateres sjeldnere | Rask interaksjon, fungerer uten tilkobling | Dataene er et øyeblikksbilde som må oppdateres manuelt eller etter en tidsplan |
| **DirectQuery** | Dataene endres ofte og du alltid trenger ferske tall     | Alltid oppdatert, ingen lokal kopi         | Tregere spørringer, krever at warehouset kjører                                |

!!! tip "Anbefaling"
    Bruk **Import** som standard. Erfaringen fra team som bruker plattformen er at Import gir
    raskere og mer stabile rapporter enn DirectQuery i praksis. Bruk **DirectQuery** bare når
    du trenger sanntidsdata eller datasettet er for stort til å importere.

## Trinn 3 — Autentiser

Ved første tilkobling blir du bedt om å autentisere deg:

1. Velg **OAuth (OIDC)** i venstre panel
2. Klikk **Sign in** — et nettleservindu åpnes
3. Logg inn med kommunebrukeren din
4. Gå tilbake til Power BI Desktop og klikk **Connect**

## Trinn 4 — Velg tabeller

1. Navigasjonsvinduet viser tilgjengelige kataloger og skjemaer i Unity Catalog
2. Utvid katalogen (for eksempel `<workspace-name>_green`) → skjemaet → velg tabellene du
   trenger
3. Klikk **Load** (Import) eller **Transform Data** (for å redigere før lasting)

## Trinn 5 — Publiser til Power BI Service (valgfritt)

1. Klikk **Publish** i Power BI Desktop
2. Velg arbeidsområde i Power BI Service (for eksempel «Teamet mitt - Prod»)
3. Rapporten og datasettet blir lastet opp

Hvis teamet versjonskontrollerer rapportene i git, bør du synkronisere via
git-integrasjonen i stedet for å publisere manuelt — se [Hvordan versjonskontrollere Power
BI-rapporter](versjonskontrollere-power-bi-rapporter.md). For automatisk oppdatering av
publiserte modeller, se [Hvordan oppdatere Power BI-modeller
automatisk](oppdatere-power-bi-modeller-automatisk.md).

## Feilsøking

| Problem                                    | Løsning                                                                                                                                                                          |
|--------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Power BI Desktop kan ikke koble til        | Sjekk at SQL Warehouse kjører og at du bruker riktig Server hostname / HTTP path                                                                                                 |
| Du ser ikke katalogen eller tabellene dine | Sjekk at du har tilgang til katalogen og skjemaet i Unity Catalog — kontakt [#dig-dataspeilet-support](https://oslokommune.slack.com/archives/C01DE13PLDP) om du mangler tilgang |

## Se også

- [Hvordan versjonskontrollere Power BI-rapporter](versjonskontrollere-power-bi-rapporter.md) —
  lagre rapporten som prosjektfil i git og synkroniser arbeidsområdet med GitHub
- [Hvordan oppdatere Power BI-modeller automatisk](oppdatere-power-bi-modeller-automatisk.md) —
  la en Databricks-jobb oppdatere den semantiske modellen etter hver pipeline-kjøring
