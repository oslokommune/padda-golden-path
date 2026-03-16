# Dokumentasjonsmaler (Diataxis)

Denne mappen inneholder maler og skriveguider for de fire dokumentasjonstypene i [Diataxis-rammeverket](https://diataxis.fr/). Filene ble opprinnelig laget som utgangspunkt for diskusjon i teamet rundt hvordan vi skal skrive de ulike typene dokumentasjon.

## Maler

Startpunkter for nye sider — kopier og fyll ut:

| Fil | Type | Beskrivelse |
|-----|------|-------------|
| `tutorial.md` | Tutorial | Læringsløp der leseren bygger noe konkret steg for steg |
| `howto.md` | How-to | Oppgaveorientert guide for å løse et spesifikt problem |
| `reference.md` | Referanse | Nøytral teknisk beskrivelse av et system eller en komponent |
| `explanation.md` | Forklaring | Kontekst og bakgrunn som svarer på «hvorfor?» |

## Skriveguider

Utdypende veiledning for hver dokumentasjonstype — les før du skriver:

| Fil | Dekker |
|-----|--------|
| `skriveguide-tutorial.md` | «Vi»-form, konkrete resultater, ingen valg, synlig progresjon |
| `skriveguide-howto.md` | Oppgavefokus, anta kompetanse, ingen forklaringer, verifiseringssteg |
| `skriveguide-reference.md` | Nøytralt språk, speile systemets struktur, komplett dekning |
| `skriveguide-explanation.md` | «Hvorfor»-spørsmål, avveininger, sammenhenger, stort bilde |

## Erstattet av Diataxis-skill?

Hvis du bruker en AI-kodingsagent (Claude Code, Cursor, Copilot o.l.) kan du installere en Diataxis-skill som gir agenten tilsvarende veiledning automatisk:

```bash
npx @smithery/cli@latest skill add wodsmith/documentation
```

For Claude Code spesifikt:

```bash
npx @smithery/cli@latest skill add wodsmith/documentation --agent claude-code --global
```

Kilden ligger på [smithery.ai/skills/wodsmith/documentation](https://smithery.ai/skills/wodsmith/documentation).

Skillen dekker det samme som skriveguidene i denne mappen, og laster inn riktig referansemateriale basert på hvilken dokumentasjonstype du jobber med. Malene (`tutorial.md`, `howto.md` osv.) kan fortsatt være nyttige som utgangspunkt for nye sider, men skriveguidene er i praksis overflødige om du har skillen installert.
