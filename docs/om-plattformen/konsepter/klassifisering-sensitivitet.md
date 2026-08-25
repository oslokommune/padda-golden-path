---
title: Klassifisering av sensitivitet
description: Hvorfor data klassifiseres som grønn, gul eller rød, og hva det betyr for tilgang og lagring.
diataxis: explanation
---

# Klassifisering av sensitivitet

Alle data på plattformen har en farge: grønn, gul eller rød. Fargen sier hvor sensitive
dataene er, og avgjør hvilken katalog de hører hjemme i. Denne siden forklarer hva nivåene
betyr, hvem som setter fargen, og hva plattformen gjør — og ikke gjør — med den. Hvordan
fargen spiller sammen med roller, er forklart i [Roller og
tilgangsstyring](roller-og-tilgangsstyring.md).

## Tre farger

Fargene er hentet fra
[trafikklysmodellen](https://www.digdir.no/informasjonsforvaltning/steg-4-vurdere-tilgangsniva/2723),
Digitaliseringsdirektoratets inndeling av datasett etter hvem som kan få tilgang:

| Farge                    | Tilgangsnivå         | Kjennetegn                                                                                                      |
|--------------------------|----------------------|-----------------------------------------------------------------------------------------------------------------|
| **Grønn** (åpne)         | Allmenn tilgang      | Alt som ikke faller i de to andre kategoriene. Hvem som helst kan få tilgang, eventuelt med vilkår for bruken.  |
| **Gul** (interne)        | Betinget tilgang     | Deles bare på vilkår eieren setter: interne arbeidsdata, forretningshemmeligheter.                              |
| **Rød** (konfidensielle) | Ikke-allmenn tilgang | Tilgangen er begrenset av lov: personopplysninger, taushetsbelagt informasjon, data av betydning for sikkerhet. |

## Hvorfor klassifisere

[Brukervilkårene](../../referanse/brukervilkaar.md) krever at teamet gjennomfører en
personvern- og risikovurdering av sin bruk av data. Klassifiseringen er det komprimerte
resultatet av den vurderingen, festet til dataene selv: Spørsmålet «kan dette deles?»
besvares én gang, og fordi hver farge har sin egen katalog, kan den grønne katalogen deles
med andre uten at den røde følger med.

## Fargen følger dataene

Klassifiseringen settes før dataene når Databricks. Et kildesystem laster opp til [landing
zone](../../referanse/landing-zone.md) under et prefiks per farge — `<sender>/red/` — og
teamets pipeline skal lese derfra inn i katalogen med samme farge — `<org>_<miljø>_red`.
Fargene er fysisk adskilt fra og med katalogen: I landing zone deler de bøtte, men hver
katalog har sin egen S3-bøtte med egen krypteringsnøkkel.

## Hvem setter fargen

Teamet, ikke Dataspeilet. Det er dataeieren som kjenner dataene godt nok til å vurdere
dem, og [dataansvarlig](../../referanse/roller-og-rettigheter.md) som forvalter kravene i
praksis. Å klassifisere krever at du vet hva som ligger i kolonnene: Inneholder datasettet
personopplysninger, også indirekte som ansattkoder eller adresser? Er noe taushetsbelagt?
Har en tredjepart rettigheter? Digitaliseringsdirektoratet anbefaler å dokumentere
lovhjemmelen for alt som er gult eller rødt, og i [forslaget til
dataproduktdefinisjon](../../referanse/dataprodukt.md) er klassifisering et obligatorisk
metadatafelt.

To tommelfingerregler: En tabell får fargen til sin mest sensitive kolonne. Og er du i
tvil, velg den strengere fargen — det er enklere å åpne opp senere enn å trekke tilbake.

## Avledede data kan få en annen farge

At kildedataene er røde, betyr ikke at alt som bygges på dem må være det. Rådataene blir i
den røde katalogen, mens et dataprodukt i gold-laget med aggregerte tall per bydel kan
vurderes på nytt og legges i grønn eller gul for deling. Men vurderingen må gjøres:
Aggregering og pseudonymisering er ikke anonymisering — i små grupper kan enkeltpersoner
gjenkjennes, og en hashet ansattkode er fortsatt en personopplysning så lenge noen kan slå
den opp.

Trenger du finere skiller *innenfor* en katalog, støtter Unity Catalog [radfiltre og
kolonnemaskering](https://docs.databricks.com/aws/en/tables/row-and-column-filters) på
tabellnivå. Det er teamets verktøy — katalogene kommer uten slike regler.

## Vanlige spørsmål

### «Betyr grønne data at alle kan se dataene?»

Nei. Grønn betyr at dataene *kunne* vært publisert åpent — ikke at de er det. Den grønne
katalogen er like isolert til workspacet ditt som den røde.

### «Kan personopplysninger ligge i gul katalog?»

Nei. Personopplysninger er lovregulert og hører hjemme i rød. Gul er for data som ikke kan
være åpne av andre grunner — interne arbeidsdata, avtaler, tredjeparts rettigheter. Data
som ennå ikke er vurdert, er ikke gule: De behandles som røde til vurderingen er gjort.

## Relatert innhold

**Forklaringer:**

- [Roller og tilgangsstyring](roller-og-tilgangsstyring.md) — fargen sier *hvor*, rollen
  sier *hvem*
- [Arkitektur](arkitektur.md) — kataloginndelingen i det store bildet

**Referanser:**

- [Landing zone](../../referanse/landing-zone.md) — fargeprefiksene der dataene kommer inn
- [Brukervilkår og ansvar](../../referanse/brukervilkaar.md) — kravet om personvern- og
  risikovurdering
- [Definisjon av dataprodukt](../../referanse/dataprodukt.md) — klassifisering som
  obligatorisk metadatafelt i forslaget
