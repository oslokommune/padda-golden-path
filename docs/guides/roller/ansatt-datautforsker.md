## Ansatt / datautforsker (grunnleggende tilgang)

Denne rollen har `USE_CATALOG` i felleskatalogen. Du kan lese data der du har fått eksplisitte rettigheter (f.eks. via gruppe/AD-gruppe), men du kan ikke opprette nye tabeller eller endre eksisterende.

### Kom i gang
- Be om tilgang til Databricks-workspace (Azure AD) og bli lagt inn i gruppen for ansatte/datautforskere.
- Logg inn på Databricks og velg riktig workspace.
- Utforsk 

### Forventninger og beste praksis
- Lesbarhet først: unngå å kjøre tunge spørringer på produksjonsklynger i arbeidstid; bruk dedikerte SQL warehouses hvis de finnes.
- Del innsikt, ikke rådata: bruk dashboards/rapporter (f.eks. Power BI) fremfor å dele CSV-er.
- Følg navngivnings- og tilgangskrav fra dataeierne; be om mer tilgang via standard prosess (ikke bruk personlige tokens som “snarvei”).
- Ikke lagre data lokalt; bruk workspace-funksjonalitet og sikre lagringsstier.
