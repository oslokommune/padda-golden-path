---
title: Versjonskontrollere Power BI-rapporter
description: Hvordan lagre Power BI-rapporter som prosjektfiler i git og synkronisere arbeidsområdet i Power BI Service med GitHub.
diataxis: how-to
---

# Versjonskontrollere Power BI-rapporter

Denne guiden viser hvordan du lagrer en rapport som et **Power BI-prosjekt** (`.pbip`),
sjekker den inn i git og synkroniserer arbeidsområdet i Power BI Service med
GitHub-repoet. Vanlige `.pbix`-filer er binære og egner seg ikke for versjonskontroll —
som prosjekt lagres rapporten og den semantiske modellen som tekstfiler, som kan
sammenlignes og gjennomgås som annen kode.

## Før du begynner

Sjekk at:

- Du har [Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop) installert
- Du har en rapport koblet til Databricks (se [Koble Power BI til
  Databricks](koble-til-power-bi.md))
- Teamet har et GitHub-repo der rapportene skal ligge
- Du kan grunnleggende git — committe, pushe og jobbe med brancher (er git nytt for deg,
  se [Git basics](https://docs.github.com/en/get-started/git-basics) fra GitHub)
- Arbeidsområdet i Power BI Service ligger på en Fabric-kapasitet (kreves for
  git-integrasjonen; eldre Power BI Premium-kapasiteter fungerer også)

## Trinn 1 — Lagre rapporten som Power BI-prosjekt

1. Aktiver funksjonen i Power BI Desktop under **File** → **Options and settings** →
   **Options** → **Preview features** → kryss av for **Power BI Project (.pbip) save
   option**. Lagringsformatet er ennå ikke ferdigstilt fra Microsofts side og må
   derfor slås på manuelt som en «preview feature».
2. Velg **File** → **Save as** og velg filtypen `.pbip`
3. Lagre prosjektet i en mappe i teamets GitHub-repo

Power BI Desktop oppretter en mappestruktur med blant annet `<navn>.Report/` og
`<navn>.SemanticModel/`, der innholdet er tekstfiler som kan versjonskontrolleres.

!!! warning "Dupliserte logicalId-er ved kopiering fra mal"
    Hver rapport og semantisk modell identifiseres av en `logicalId` i fila `.platform`. Hvis
    du har opprettet prosjektet ved å kopiere en mal eller et eksisterende prosjekt, arver
    kopien de samme ID-ene, og synkroniseringa til Power BI Service feiler. Slik retter du
    det:

    1. Generer to nye GUID-er, for eksempel med `[guid]::NewGuid()` i PowerShell eller
       `uuidgen` i en terminal
    2. Åpne fila `.platform` i `<navn>.Report/`-mappa og erstatt verdien i
       `logicalId`-feltet med den ene GUID-en
    3. Gjør det samme i `<navn>.SemanticModel/`-mappa med den andre GUID-en

    De to ID-ene må være ulike, og de må være unike i arbeidsområdet.

## Trinn 2 — Parametriser tilkoblinga for stage og prod (valgfritt)

Hvis teamet har både stage- og prod-workspace i Databricks, bør tilkoblingsdetaljene ligge
i parametere i stedet for å være hardkodet. Da kan samme rapport pekes mot stage eller
prod uten å endre selve rapporten:

1. Klikk **Transform data** for å åpne Power Query-editoren
2. Velg **Manage Parameters** → **New parameter** og opprett to tekstparametere, for
   eksempel `ServerHostname` og `HttpPath`
3. Sett verdiene til tilkoblingsdetaljene for stage (se [Finn
   tilkoblingsdetaljer](koble-til-power-bi.md#trinn-1-finn-tilkoblingsdetaljer))
4. Rediger kildesteget (**Source**) for hver tabell slik at det bruker parameterne i
   stedet for de hardkodede verdiene

I Power BI Service kan parameterne endres per semantisk modell under **Settings** →
**Parameters**. Bruker teamet en deployment pipeline til å flytte rapporten fra stage- til
prod-arbeidsområdet, kan parameterverdiene byttes automatisk med en distribusjonsregel
(deployment rule).

## Trinn 3 — Koble arbeidsområdet til GitHub-repoet

Med git-integrasjonen i Power BI Service synkroniseres arbeidsområdet mot en branch i
GitHub-repoet, i stedet for at du publiserer manuelt fra Power BI Desktop:

1. Gå til arbeidsområdet i Power BI Service
2. Åpne **Workspace settings** → **Git integration**
3. Velg **GitHub** som leverandør og koble til repoet, branchen og mappa der rapporten
   ligger

Når du har committet og pushet endringer til branchen, åpner du **Source control**-panelet
i arbeidsområdet og klikker **Update all** for å laste inn den nye versjonen. Endringer
gjort direkte i Power BI Service kan tilsvarende committes tilbake til repoet fra samme
panel.

## Feilsøking

| Problem                                               | Løsning                                                                                                                       |
|-------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Dupliserte `logicalId`-er ved git-synkronisering      | Generer nye GUID-er og erstatt `logicalId` i `.platform`-filene, se [Trinn 1](#trinn-1-lagre-rapporten-som-power-bi-prosjekt) |
| Arbeidsområdet viser ikke endringer fra GitHub        | Åpne **Source control**-panelet og klikk **Update all**; sjekk at arbeidsområdet er koblet til riktig branch og mappe         |
| Git-integrasjon er ikke tilgjengelig i arbeidsområdet | Sjekk at arbeidsområdet ligger på en Fabric-kapasitet, og at git-synkronisering er slått på i tenant-innstillingene           |

## Se også

- [Koble Power BI til Databricks](koble-til-power-bi.md) — koble Power BI Desktop til SQL
  Warehouse og publiser rapporten
- [Oppdatere Power BI-modeller automatisk](oppdatere-power-bi-modeller-automatisk.md) —
  la en Databricks-jobb oppdatere den semantiske modellen etter hver pipeline-kjøring
