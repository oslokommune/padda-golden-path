# Mal: Forklaring (Explanation)

Forklaringsdokumentasjon **bygger forståelse**. Den er diskursiv, reflekterende
og ment for å leses — ikke for å skummes etter raske svar.

## Prinsipper

- **Skriv prosa, ikke sjekklister.** Forklaringer er tekst leseren *leser*,
  ikke lister de *skanner*. Bruk sammenhengende avsnitt. Spar kulepunkter
  til reelle lister av elementer.
- **Svar på «hvorfor», ikke «hvordan».** Hvis du merker at du skriver steg,
  er du i ferd med å skrive en how-to. Lenk til den i stedet.
- **Gi kontekst.** Koble temaet til det større bildet — forretningsbehov,
  tekniske begrensninger, historiske beslutninger.
- **Anerkjenn avveininger.** Ekte designbeslutninger innebærer kompromisser.
  Vær ærlig om dem.
- **Tillat perspektiv.** Det er greit å si «vi valgte X fordi ...» —
  forklaring er det ene stedet der meninger og resonnement hører hjemme.

## Faste elementer

### Frontmatter

```yaml
---
title: Om medallion-arkitekturen
description: >-
  Hvorfor plattformen bruker bronze-, silver- og gold-lag, og hvordan
  de henger sammen med datakvalitet og eierskap.
diataxis: explanation
tags:
  - bearbeide-data
---
```

### Åpning

Et kort avsnitt som sier hva denne siden hjelper leseren med å forstå, og
hvorfor det er viktig. Ikke «denne siden forklarer ...» — bare forklar.

### «Relatert innhold»-seksjon

Lenker til relevante guider og referansesider.

## Kjerne- og valgfrie seksjoner

Ikke alle forklaringer trenger alle seksjoner. Kjernen er:

- **Det store bildet** — hvordan temaet passer inn i plattformen
- **Hvorfor dette finnes** — resonnementet bak designet eller konseptet

Disse er valgfrie, bruk når de er relevante:

- **Hvordan delene henger sammen** — relasjoner mellom komponenter
- **Designvalg og avveininger** — alternativer som ble vurdert, hvorfor ett ble valgt
- **Begrensninger** — hva dette ikke løser
- **Historikk eller bakgrunn** — organisatorisk eller teknisk kontekst
- **Vanlige misforståelser** — korriger utbredte feiloppfatninger

## Eksempelstrukturer

### A: Arkitekturbeslutning (f.eks. «Om medallion-arkitekturen»)

Bruk når du forklarer et designvalg. Leseren vil forstå *hvorfor* ting er
som de er.

```markdown
# Om medallion-arkitekturen

Dataplattformen organiserer data i tre lag: bronze, silver og gold.
Denne strukturen — ofte kalt medallion-arkitekturen — styrer hvordan
data beveger seg fra råformat til forretningsklare datasett.

## Det store bildet

Når en virksomhet laster opp data til plattformen, går dataene gjennom
en forutsigbar reise. Bronze-laget tar imot data akkurat som de er,
uten endringer. Silver-laget renser og standardiserer. Gold-laget
tilpasser data til konkrete bruksområder som rapportering eller analyse.

Denne tredelingen finnes fordi ...

    [sammenhengende avsnitt som forklarer hvorfor, ikke kulepunkter]

## Hvorfor tre lag?

Det hadde vært enklere å transformere direkte fra rådata til ferdige
datasett. Vi valgte tre lag fordi ...

    [resonnement om sporbarhet, gjenbruk, feilhåndtering]

Et alternativ vi vurderte var ...

    [ærlig drøfting av avveininger]

## Hva hvert lag inneholder

    [beskrivelse av bronze, silver, gold — hva som skjer i hvert lag,
     hvem som eier det, hva slags data man finner der]

## Begrensninger

Medallion-arkitekturen løser ikke alt ...

    [ærlig om hva den ikke dekker]

## Relatert innhold

- [Bronze til silver](../...) for konkrete transformasjonssteg
- [Referanse: Navnekonvensjoner](../...) for tabell- og skjemanavn
```

### B: Konseptforklaring (f.eks. «Om dataklassifisering»)

Bruk når du forklarer et konsept leseren trenger å forstå for å bruke
plattformen riktig. Mindre om designvalg, mer om «hva er dette og hvorfor
bør jeg bry meg».

```markdown
# Om dataklassifisering

All data som lastes inn i plattformen klassifiseres etter
konfidensialitetsnivå: grønn, gul eller rød. Klassifiseringen
bestemmer hvem som kan se dataene og hvor de lagres.

## Hvorfor klassifisering?

Oslo kommune forvalter data som spenner fra åpne datasett til
sensitive personopplysninger. Klassifiseringen sikrer at ...

    [sammenhengende avsnitt]

## De tre nivåene

### Grønn — åpne data

    [hva dette betyr i praksis, eksempler]

### Gul — interne data

    [hva dette betyr, typiske datasett, tilgangskrav]

### Rød — konfidensielle data

    [hva dette betyr, personopplysninger, strenge krav]

## Vanlige misforståelser

### «Alle mine data er grønne fordi de ikke inneholder personnummer»

Klassifisering handler ikke bare om direkte personidentifisering ...

    [korrigering med resonnement]

## Relatert innhold

- [Laste opp filer til landing zone](../...) for hvordan klassifisering
  påvirker hvilken mappe du bruker
- [Referanse: Landing zone-struktur](../...) for mappestier per nivå
```

### C: Forretningsrettet forklaring (f.eks. «Hva dataplattformen tilbyr»)

Bruk for sider rettet mot beslutningstagere eller nye brukere. Mindre teknisk
dybde, mer fokus på verdi og egnethet.

```markdown
# Hva dataplattformen tilbyr

Padda er en dataplattform for virksomheter i Oslo kommune som
trenger å hente inn, bearbeide og dele data programmatisk.

## Hvem er plattformen for?

    [beskrivelse av målgruppe, hva slags behov den dekker,
     hva slags kompetanse som forventes]

## Hva du kan gjøre

    [konkrete bruksområder, skrevet som korte avsnitt — ikke en
     funksjonsliste]

## Hva plattformen ikke er

    [ærlig avgrensning — ikke Fabric, ikke en BI-plattform,
     ikke en ferdigløsning uten koding]

## Relatert innhold

- [Er Databricks-plattformen riktig for deg?](../...) for en
  konkret vurdering av om plattformen passer ditt behov
- [Kom i gang](../...) hvis du er klar til å prøve
```
