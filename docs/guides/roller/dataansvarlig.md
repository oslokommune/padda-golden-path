## Dataansvarlig (data owner)

Rollen er ansvarlig for struktur, tilgang og datakvalitet i sitt domene.

### Kom i gang
- Verifiser at du er lagt inn som data owner i riktig katalog.
- Opprett og navngi schema etter avtalt konvensjon (`<domene>_<område>`), og dokumentér formål, hjemmel og kontaktpunkt.
- Sett grunnleggende tilgang: gi `USE SCHEMA`/`CREATE TABLE` til dataanalytikere og `USE_CATALOG` til ansatte ved behov; gi `ALL PRIVILEGES` kun til driftsroller etter avtale.
- Etabler datasettlivssyklus: Bronze/Silver/Gold, kvalitetssjekker og sletting/arkivering.

### Løpende ansvar
- Forvalte tilgang og følge sikkerhetskrav (sensitivitet, persondata).
- Godkjenne nye tabeller og bryte ned eierskap til schema-nivå.
- Sikre dokumentasjon (datakatalog, README, feltbeskrivelser) og kontaktpunkt.
- Følge naming- og governance-prinsipper fra plattformteamet.
