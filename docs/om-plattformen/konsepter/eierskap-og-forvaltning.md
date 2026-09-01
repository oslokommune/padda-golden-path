---
title: Eierskap og forvaltning
description: Hvem som eier dataene på plattformen, hva eierskapet innebærer, og hvordan beslutninger om deling tas.
diataxis: explanation
---

# Eierskap og forvaltning

Plattformen gir teamene verktøy for å bygge og drifte [dataprodukter](dataprodukter.md),
men eier ikke dataene som flyter gjennom den. Denne siden forklarer hvem som eier hva, hva
eierskapet innebærer, hvor grensa mot Dataspeilet går, og hvordan beslutninger om å dele
data tas. Hva hver rolle i workspacet kan gjøre teknisk, står i referansen [Roller og
rettigheter](../../referanse/roller-og-rettigheter.md).

## Tre eiere for ett dataprodukt

[Forslaget til dataproduktdefinisjon](../../referanse/dataprodukt.md#forvaltning) deler
eierskapet i tre roller:

- **Dataprodukteieren** svarer for formålet: hvorfor dataproduktet finnes, hvilken hjemmel
  det bygger på, hvordan det er klassifisert, og hvem som får bruke det til hva.
- **Dataforvalteren** svarer for innholdet fra dag til dag: kvalitet, dokumentasjon,
  begreper, avvik og brukerstøtte.
- **Den tekniske eieren** svarer for at det virker: pipelines, skjemaendringer, overvåking
  og kobling til plattformressursene.

Grunnen til å skille dem er at ansvaret sjelden ligger hos én person. Den som kjenner
hjemmelen og formålet, sitter gjerne nær kildesystemet og fagområdet, og kan være utenfor
teamet som bygger pipelinen. [Brukervilkårene](../../referanse/brukervilkaar.md) kaller
denne rollen dataeier, og krever at dataeieren har godkjent opplastingen og kjenner
risikoen ved plattformen før data lastes opp.

Noen ganger har én person flere roller, spesielt i små team. Det er greit, så lenge det er
avklart hvem som svarer for hva. [Målgruppesiden](../overordnet/maalgrupper.md) stiller
nettopp krav om en dataprodukteier og om kapasitet til forvaltning, ikke bare første
leveranse.

På plattformen får dataforvalteren, og ofte dataprodukteieren, rettighetene sine gjennom
rollen **dataansvarlig**. Den tekniske eieren er utviklerne i teamet. Hvorfor rollene er
delt slik, er forklart i [Roller og tilgangsstyring](roller-og-tilgangsstyring.md).

## Hva eierskapet innebærer

Å eie et dataprodukt er å svare for det over tid. Konkret betyr det å:

- **Avklare formål og hjemmel** før data lastes opp. Brukervilkårene krever at teamet
  gjennomfører en egen personvern- og risikovurdering av sin bruk av data.
- **Klassifisere** dataene og legge dem i riktig katalog, se [Klassifisering av
  sensitivitet](klassifisering-sensitivitet.md).
- **Dokumentere** slik at brukere forstår innholdet uten å spørre: beskrivelser på
  tabeller og kolonner i Unity Catalog, og et kontaktpunkt for spørsmål.
- **Følge opp kvaliteten.** Datakvalitet er et bevegelig mål som krever løpende
  oppmerksomhet, ikke et engangstiltak, se [Datakvalitet](datakvalitet.md).
- **Styre livsløpet.** Hvor lenge data skal oppbevares, når et dataprodukt fases ut, og
  når data slettes, følger av teamets egen personvern- og risikovurdering. Plattformen
  setter ingen frister og tar ikke [backup](../../referanse/backup.md) av tabellene;
  teamet må selv sørge for redundans der det trengs.

## Dataspeilet eier det tekniske

Digitaliseringsdirektoratets veileder for orden i eget hus råder virksomheter til å
delegere ansvaret for data «ut der kunnskapen ligger», og å begrense IT-avdelingens ansvar
«til det rent tekniske» ([Steg 7: Styre og
forvalte](https://www.digdir.no/informasjonsforvaltning/steg-7-styre-og-forvalte/2727)).
Plattformen er bygget etter samme prinsipp.

Dataspeilet eier workspaces, kataloger, landing zones og nettverk, det som bør være likt
for alle team. Når et workspace settes opp, oppretter Dataspeilet katalogene og overfører
eierskapet til teamet. Fra da av er alt inne i katalogen teamets: skjemaer, tabeller,
eierskap og tilganger. Dataspeilet ser ikke på innholdet, vurderer ikke kvaliteten og tar
ikke stilling til om data kan deles.

Konsekvensen er at spørsmål som «kan vi dele dette datasettet?» og «er dette
personopplysninger?» hører hjemme hos dataprodukteieren, gjerne med støtte fra avdelingen
for jus, informasjonssikkerhet og personvern (JIPI).

## Eierskap er også teknisk

Eierskap er ikke bare en rolle på papiret. Hvert objekt i Unity Catalog har [én
eier](https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/ownership),
og eieren har alle rettigheter til objektet, inkludert retten til å gi andre tilgang.
Objekter eies i utgangspunktet av den som opprettet dem. En tabell skrevet av en
produksjonspipeline eies dermed av service principalen som kjørte den, ikke av utvikleren.

Det gir to føringer. Eierskap bør ligge hos grupper, ikke personer, slik at det ikke
forsvinner når noen bytter team. Og eierskap og tilganger bør deklareres i koden sammen
med tabellene de gjelder, i bundlen, slik at de deployes, versjoneres og gjennomgås på
samme måte som resten av dataproduktet. Da er svaret på «hvem eier denne tabellen?» alltid
å finne i Git.

## Tilgangsbeslutninger

Å gi noen tilgang til data er en beslutning dataprodukteieren tar, og som teamet setter i
verk. Hvordan det skjer, avhenger av hvor mottakeren er:

- **I samme workspace** gir teamet tilgang selv, ved å tildele rettigheter på skjema eller
  tabell til en gruppe.
- **I et annet workspace** er ikke katalogen synlig før Dataspeilet har knyttet den til
  mottakerens workspace. Deling på tvers av team er derfor en bestilling, et bevisst steg
  som følger av at workspacet er plattformens [enhet for isolasjon](arkitektur.md#bearbeiding-ett-workspace-per-team-og-milj).
- **Utenfor plattformen** bør konsumenter møte dataene som ferdige dataprodukter, for
  eksempel via Power BI eller
  [Fabric-plattformen](../overordnet/velg-riktig-plattform.md), ikke ved å slippes inn i
  workspacet.

Tilgang og bruksrett er to forskjellige ting. At noen kan lese en tabell, sier ikke hva de
har lov til å bruke den til: om den kan kopieres, sammenstilles med andre kilder, deles
videre eller brukes til å trene modeller. Forslaget til dataproduktdefinisjon skiller
derfor mellom tilgangsmodell og [bruksrett](../../referanse/dataprodukt.md#bruksrett), og
krever at bruksretten dokumenteres særskilt når data deles på tvers av team. Konsumenten
påtar seg et ansvar i retur: å bruke dataene til det avtalte formålet, ikke dele dem
videre, og melde fra om feil.

## Vanlige spørsmål

### «Kan Dataspeilet avgjøre om vi kan dele et datasett?»

Nei. Dataspeilet eier plattformen, ikke dataene, og kjenner verken hjemmelen eller
innholdet. Beslutningen ligger hos dataprodukteieren.

### «Vi er tre personer. Trenger vi tre eiere?»

Nei, men det trengs tre avklarte ansvar: formål og hjemmel, innhold og drift. Det holder
at én person dekker alle tre, så lenge det er tydelig hvem som svarer for hva.

### «Hva skjer med dataene når teamet legges ned?»

Eierskapet må overføres før teamet forsvinner, både det organisatoriske og det tekniske i
Unity Catalog. Dataprodukter uten eier oppfyller ikke [kravene til et
dataprodukt](dataprodukter.md) og bør fases ut eller slettes.

## Relatert innhold

**Forklaringer:**

- [Dataprodukter](dataprodukter.md) — kravene til et dataprodukt, inkludert definert eier
- [Roller og tilgangsstyring](roller-og-tilgangsstyring.md) — hvorfor tilgang følger
  roller og grupper
- [Klassifisering av sensitivitet](klassifisering-sensitivitet.md) — hvem som setter
  fargen, og hva den betyr

**Referanser:**

- [Definisjon av dataprodukt](../../referanse/dataprodukt.md) — rollene dataprodukteier,
  dataforvalter og teknisk eier, livssyklus og bruksrett
- [Brukervilkår og ansvar](../../referanse/brukervilkaar.md) — ansvaret teamet påtar seg
- [Roller og rettigheter](../../referanse/roller-og-rettigheter.md) — rettighetene til
  workspace-admin, dataanalytiker og dataansvarlig
