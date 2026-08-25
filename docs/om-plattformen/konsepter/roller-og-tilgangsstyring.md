---
title: Roller og tilgangsstyring
description: Hvorfor plattformen bruker rollebasert tilgangsstyring, og hvordan roller henger sammen med sensitivitetsklassifisering.
diataxis: explanation
---

# Roller og tilgangsstyring

Tilgang på plattformen gis som hovedregel ikke til enkeltpersoner, men følger roller — og
rollene følger grupper i Oslo kommunes Entra ID. Enkelttilganger forekommer, men de er
unntaket. Denne siden forklarer hvorfor tilgangsstyringen er bygget slik, hvordan den
henger sammen med sensitivitetsklassifiseringen, og hvilke avveininger som ligger bak. Hva
hver enkelt rolle kan gjøre, står i referansen [Roller og
rettigheter](../../referanse/roller-og-rettigheter.md).

## Hvorfor roller og ikke enkelttilganger

Det enkleste svaret på «kan jeg få tilgang til disse dataene?» er å gi personen som spør
en tilgang. Det fungerer helt til det har skjedd noen hundre ganger. Da har plattformen et
lappeteppe av enkelttilganger som ingen lenger har oversikt over: Spørsmålet «hvem kan
lese denne tabellen?» krever detektivarbeid, og tilganger råtner — folk bytter team og
beholder rettigheter de ikke lenger skulle hatt.

Rollebasert tilgangsstyring snur dette på hodet. Tilgangene beskrives én gang per rolle,
og personer får dem ved å være medlem av gruppa som svarer til rollen. Den som blir med på
et team, arver alt rollen skal ha. Den som slutter, mister alt samtidig. Og spørsmålet
«hvem har tilgang?» besvares ved å liste gruppemedlemmene.

Av samme grunn gis tilgang på teamnivå, ikke individnivå. Team [meldes inn via
Slack](../../kom-i-gang/slik-faar-du-tilgang.md), og den som melder inn, godtar
[brukervilkårene](../../referanse/brukervilkaar.md) på vegne av hele teamet. Plattformen
er bygget for team som sammen forvalter et dataområde over tid — ikke for enkeltpersoner
med hver sin tilgangsliste.

## Én kjede fra kommunebruker til tabell

Identiteter og grupper bor i Entra ID og forvaltes av kommunens sentrale
identitetsforvaltning. Databricks oppretter aldri egne brukere, men leser dem fra Entra
ID, og gruppemedlemskapene avgjør hvilke workspaces du ser og hva du kan gjøre i Unity
Catalog — leddene i kjeden er beskrevet i [Roller og
rettigheter](../../referanse/roller-og-rettigheter.md). Plattformen har dermed ingen egne
brukere eller passord: Du logger inn med kommunebrukeren din, og når den deaktiveres,
forsvinner tilgangen på plattformen med den. Tilgangsstyringen har én kilde til sannhet,
og den ligger der identiteter allerede forvaltes.

Kjeden ender i ett bestemt workspace, og workspacet er plattformens enhet for isolasjon:
Katalogene dine er bundet til workspacet ditt, og andre team ser dem ikke uten at dere
eksplisitt har delt dem. At mange team bruker samme plattform, betyr altså ikke at de ser
hverandres data.

## Roller er ansvarsnivåer

Hvert workspace har tre roller: **workspace-admin**, **dataanalytiker** og
**dataansvarlig**. Rollene er ikke bare lister med rettigheter, men en beskrivelse av hvem
som har hvilket ansvar — og skillene mellom dem går der ansvaret i praksis skifter hender.

Det tydeligste skillet er mellom workspace-admin og dataansvarlig. Den som drifter
workspacet — ressurser, jobber og gruppemedlemskap — er sjelden den som kjenner dataene
godt nok til å vurdere kvalitet, sensitivitet og hvem som bør få se hva. Derfor er
dataansvarlig en egen rolle: Fageieren eier skjemaene i sitt domene og styrer struktur,
tilgang og kvalitet der, uten å måtte være administrator for hele workspacet.

Skillet mellom dataanalytiker og dataansvarlig går ved produksjon. Analytikeren utforsker
data, lager egne tabeller og bygger [dataprodukter](dataprodukter.md), men skriver ikke
til produksjonsskjemaer — det er forbeholdt pipelines. Det som ligger i produksjon, har
kommet dit gjennom kode, og dataansvarlig avgjør hvilke tabeller som skal finnes der.

## Sensitivitet avgjør hvor, roller avgjør hvem

Rollene er bare den ene aksen i tilgangsmodellen. Den andre er
[sensitivitetsklassifiseringen](klassifisering-sensitivitet.md): Data klassifiseres som
grønne (åpne), gule (interne) eller røde (konfidensielle), og nivået avgjør hvilken
katalog dataene hører hjemme i. Skillet følger data helt fra [landing
zone](../../referanse/landing-zone.md), og hvert workspace har én katalog per farge.

De to aksene svarer på ulike spørsmål. Fargen sier *hvor* data skal ligge, og hvilke krav
til lagring og deling som følger med. Rollen sier *hvem* som får gjøre hva — og den
gjelder for hele workspacet, ikke per farge. En dataanalytiker har med andre ord samme
tilgang i teamets røde katalog som i den grønne. Fargen er ikke en tilgangssperre innad i
teamet; den er en merkelapp som får betydning når dataene skal deles videre, og når noen
utenfor teamet skal ha tilgang.

Det har to konsekvenser. Det er teamet, ikke plattformen, som avgjør hvem i teamet som
skal jobbe med røde data — den som blir medlem av gruppa, får alt rollen gir. Og
kataloginndelingen gjør det mulig å dele grovkornet: Den grønne katalogen kan deles med
andre uten at den røde følger med.

Deling skjer dessuten i to trinn. Rollen katalogbruker gir lesetilgang til *metadata* —
hvilke kataloger, skjemaer og tabeller som finnes — slik at det går an å oppdage hvilke
data som eksisterer. Innholdet i tabellene krever egen, eksplisitt tildeling. Å vite at en
tabell finnes, er dermed noe annet enn å kunne lese den.

## Avveininger

Som resten av [arkitekturen](arkitektur.md) prioriterer tilgangsmodellen noen hensyn på
bekostning av andre:

- **Grove skiller fremfor finmaskede regler.** Tilgang styres på katalognivå. Det er
  enkelt å forstå og revidere, men trenger et team finere skiller — for eksempel at bare
  noen skal se et bestemt rødt skjema — må dataansvarlig eller workspace-admin sette dem
  opp selv på skjema- eller tabellnivå.

- **Isolasjon fremfor friksjonsfri deling.** Kataloger er bundet til sitt workspace, og
  ingen andre team ser dem uten eksplisitt tildeling. Det gjør tilgangsbeslutninger lokale
  og trygge, men deling på tvers krever et bevisst steg.

- **Teamnivå fremfor individnivå.** For et team er terskelen lav; for en enkeltperson som
  bare vil titte på et datasett, er den høyere. Det er villet: Databricks-tilgang er for
  teamet som bygger og forvalter dataproduktene. Enkeltbrukere og andre etater som skal
  *bruke* dem, skal som regel møte dataene som ferdige dataprodukter — i praksis via
  [Fabric-plattformen](../overordnet/velg-riktig-plattform.md) eller Power BI — ikke ved å
  slippes inn i workspacet.

- **Én kilde til sannhet fremfor rask endring.** Fordi gruppene bor i Entra ID og
  opprettes av kommunens identitetsforvaltning, kan ikke teamet selv lage en ny gruppe
  eller rolle når behovet oppstår. Det er prisen for at tilgang alltid kan spores tilbake
  til én forvaltet identitet — nye grupper er en bestilling, ikke et klikk.

## Relatert innhold

**Forklaringer:**

- [Arkitektur](arkitektur.md) — det overordnede bildet, inkludert workspace-isolasjon og
  kataloginndeling
- [Klassifisering av sensitivitet](klassifisering-sensitivitet.md) — grønn, gul og rød,
  og hva nivåene betyr

**Referanser:**

- [Roller og rettigheter](../../referanse/roller-og-rettigheter.md) — gruppene, rollene
  og tilgangene i detalj
- [Brukervilkår og ansvar](../../referanse/brukervilkaar.md) — ansvaret teamet påtar seg

**Kom i gang:**

- [Slik får du tilgang](../../kom-i-gang/slik-faar-du-tilgang.md) — meld inn teamet og
  logg inn
