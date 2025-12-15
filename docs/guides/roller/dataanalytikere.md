## Dataanalytiker

Rollen har `USE_CATALOG`, `USE SCHEMA` og `CREATE TABLE`. Du kan lese, lage egne tabeller og prototyper, men endringer i produksjonsskjemaer må koordineres med dataeier.

### Kom i gang
- Sørg for at du er medlem av gruppen for dataanalytikere og har tilgang til relevant katalog/schema.
- Bruk SQL warehouse for BI/spørring og all-purpose cluster for notatbøker/ELT.
- Opprett egne tabeller i avtalt schema. Publisering til felles schema skjer via review med dataeier.

### Beste praksis
- **Skjemaer:** Bruk dedikerte schema for eksperimentering (`<team>_sandbox`) og hold produksjonsschema rent.
- **Tabeller:**
- **Ytelse:** Partisjoner og optimaliser (ZORDER) større Delta-tabeller. Unngå unødvendige fullskann.
- **Datahygiene:** Rydd etter bruk; dropp midlertidige tabeller og begrens antall versjoner.
- **Deling:** Eksponer rapporter/dashboards via godkjente verktøy (Power BI) og del lenker – ikke råfiler.
