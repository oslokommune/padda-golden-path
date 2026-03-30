---
title: Hva tilbyr dataplattformen?
description: Hva plattformen gir deg som utvikler eller analytiker, og hva som er ditt ansvar.
diataxis: explanation
---

# Hva tilbyr dataplattformen?

Mange virksomheter i Oslo kommune har behov for avansert databehandling som går utover det standardverktøy tilbyr. Transformasjoner som krever kode, sammenstillinger på tvers av kilder, kvalitetssikring med forretningslogikk, og automatiserte pipelines som kjører uten manuell innsats.

Data engineering-plattformen gir utviklere og kodende analytikere et arbeidsmiljø for å gjøre nettopp dette — programmatisk, med full kontroll, og med innebygd støtte for sikkerhet, deploy og overvåking.

Mye av det som bygges på plattformen vil være [dataprodukter](../konsepter/dataprodukter.md) — behandlede, dokumenterte datasett med en definert eier, klare til å brukes av andre.

<div class="grid cards" markdown>

-   **For deg som koder**

    - Notebooks og pipelines med SQL og Python
    - Brolagte stier fra rådata til ferdig dataprodukt
    - Automatisert deploy via CI/CD og Databricks Asset Bundles
    - Serverless compute — ingen cluster-administrasjon
    - Sikker lagring og tilgangsstyring via Unity Catalog
    - Overvåking, logging og Slack-varsling ut av boksen

-   **For deg som leder**

    - Mer presis beslutningsstøtte — styringsdata du kan stole på
    - Raskere vei fra behov til innsikt
    - Mindre personavhengighet — kunnskap ligger i kode, ikke i hoder
    - Lavere risiko for feil i rapporter og analyser
    - Dataprodukter som oppdateres automatisk
    - Innebygd sikkerhet og etterlevelse

</div>

## Raskere fra behov til dataprodukt

- Selvbetjente verktøy for hele datareisen: innhenting, transformasjon, deling
- Ferdiglagde maler og brolagte stier som tar deg fra idé til produksjon
- Mindre ventetid — du trenger ikke vente på andre team for å komme i gang

## Mindre manuelt arbeid

- Automatisert deploy, logging og overvåking
- Feil fanges tidlig — før sluttbrukerne oppdager dem
- Standardiserte pipelines som er enklere å vedlikeholde og feilsøke

## Innebygd sikkerhet og kvalitet

- Tilgangsstyring, kryptering og sporbarhet er en del av verktøyene
- Du slipper å bygge egne sikkerhetsløsninger
- Juridiske vurderinger kan knyttes direkte til dataproduktene

## Fellesskap og deling

- Felles standarder gjør det enklere å gjenbruke data og kode på tvers
- Dokumentasjon, kodeeksempler og beste praksis deles i et faglig community
- Du bygger ikke alene — du bygger på det andre allerede har løst

<!-- Bilde: visuell oversikt over plattformens byggeklosser — f.eks. en enkel arkitekturtegning med innhenting, transformasjon, lagring, deling, overvåking som lag -->

---

## Ditt ansvar

Plattformen er et fundament, ikke en ferdig løsning. Du og teamet ditt har ansvar for:

- **[Dataproduktene dine](../konsepter/dataprodukter.md)** — utvikle, dokumentere og forvalte dem over tid
- **[Datakvalitet](../konsepter/klassifisering-datakvalitet.md)** — rette feil i datagrunnlaget og følge opp avvik
- **[Juridiske vurderinger](../konsepter/klassifisering-sensitivitet.md)** — avgjøre hva som kan deles, med hvem, og hvorfor
- **[Tilgangsbeslutninger](../konsepter/roller-og-tilgangsstyring.md)** — vurdere om og når data kan tilgjengeliggjøres

Plattformen gjør det lettere å gjøre rett. Men ansvaret for dataene ligger hos deg som eier dem.
