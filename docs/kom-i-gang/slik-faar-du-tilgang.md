---
title: Slik får du tilgang
description: Meld inn teamet ditt via Slack og godta brukervilkårene for å få tilgang til dataplattformen.
diataxis: tutorial
---

# Slik får du tilgang

Tilgang til dataplattformen gis på teamnivå. I dette steget melder du inn teamet ditt via
Slack. Når Dataspeilet har behandlet innmeldinga, har teamet fått miljøene sine i
Databricks, og du kan logge inn med kommunebrukeren din.

## Før du starter

- Les [brukervilkårene](../referanse/brukervilkaar.md). Den som melder inn teamet, godtar
  vilkårene på vegne av hele teamet.
- Ha klart for deg hvem som er på teamet: utviklere, eventuelle analytikere og
  dataeier/dataansvarlig.

## Meld inn teamet

1. Gå til Slack-kanalen
   [#dig-dataspeilet-support](https://oslokommune.slack.com/archives/C01DE13PLDP).

2. Klikk på lynikonet øverst i kanalen og start workflowen **Nytt team i Databricks**.

3. Fyll ut og send inn skjemaet. Her bekrefter du at teamet godtar brukervilkårene, og du
   oppgir blant annet hvem som er på teamet og hvilke miljøer dere trenger.

## Hva skjer videre?

Dataspeilet tar imot innmeldinga og setter opp det teamet trenger: miljøer i Databricks og
tilgang for alle teammedlemmene du oppga i skjemaet. De tar kontakt i samme kanal hvis de
trenger mer informasjon, og gir beskjed når alt er klart.

## Logg inn

Når du har fått beskjed om at alt er klart, går du til
[login.databricks.com](https://login.databricks.com), velger **Continue with Microsoft**
og logger inn med kommunebrukeren din. Databricks bruker Oslo kommunes Entra ID som
identitetsleverandør, så du trenger ikke eget passord for Databricks, og
flerfaktorautentisering følger kommunens vanlige oppsett.

Etter pålogging skal du få opp en liste over workspacene du har fått tilgang til.

Lurer du på hva du kan gjøre i workspacet? Se
[Roller og rettigheter](../referanse/roller-og-rettigheter.md).

## Neste steg

Nå som du har tilgang, er neste steg å [sette opp utviklingsmiljøet](dev-setup.md).
