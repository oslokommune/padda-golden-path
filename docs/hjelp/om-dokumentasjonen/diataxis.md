---
title: Diataxis
description: Hvordan vi bruker Diataxis-rammeverket til å strukturere dokumentasjonen for dataplattformen.
diataxis: explanation
---

# Diataxis — vår dokumentasjonsmodell

Dokumentasjonen for dataplattformen følger [Diataxis](https://diataxis.fr/)-rammeverket. Diataxis deler dokumentasjon i fire typer basert på hva leseren trenger:

| Type | Leseren vil ... | Hos oss |
|------|-----------------|---------|
| **Tutorial** | Lære noe nytt gjennom å gjøre | [Kom i gang](../../kom-i-gang/index.md) |
| **How-to** | Løse en konkret oppgave | [Guider](../../guider/index.md) |
| **Explanation** | Forstå hvorfor noe er som det er | [Om plattformen](../../om-plattformen/index.md) |
| **Reference** | Slå opp fakta mens de jobber | [Referanse](../../referanse/index.md) |

Å holde typene adskilt gjør det lettere å skrive tydelig — og lettere for leseren å finne det de leter etter.

## Maler

Vi har en mal for hver dokumentasjonstype. Kopier den som passer og fyll ut:

- [Mal: Tutorial](mal-tutorial.md) — veiledet læringsopplevelse
- [Mal: How-to](mal-howto.md) — oppgaverettede anvisninger
- [Mal: Forklaring](mal-forklaring.md) — kontekst, bakgrunn og "hvorfor?"
- [Mal: Referanse](mal-referanse.md) — nøytral faktabeskrivelse

Hver mal markerer seksjoner som **[OBLIGATORISK]** eller **[FRIVILLIG]**, og viser eksempler på innholdet som hører hjemme der. Info-boksen øverst oppsummerer prinsippene for typen — slett den når du begynner å skrive.

## [Frontmatter](https://zensical.org/docs/authoring/frontmatter/)

Alle sider har denne frontmatteren:

```yaml
---
title: Sidetittel
description: Beskrivelse for søkemotorer.
diataxis: tutorial  # tutorial | how-to | explanation | reference
---
```

For stub-sider som ikke er skrevet ennå, legg til `icon: lucide/construction`.
