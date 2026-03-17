# Dokumentasjonsmaler (Diataxis)

Denne mappen inneholder maler og skriveguider for de fire dokumentasjonstypene i [Diataxis-rammeverket](https://diataxis.fr/). Filene ble opprinnelig laget som utgangspunkt for diskusjon i teamet rundt hvordan vi skal skrive de ulike typene dokumentasjon.

## Maler

Startpunkter for nye sider — kopier og fyll ut:

| Fil | Type | Bruk for |
|-----|------|----------|
| `tutorial.md` | Tutorial | Veiledet læringsopplevelse der leseren bygger noe steg for steg. Sider under **Kom i gang**. |
| `howto.md` | How-to | Oppgaverettede anvisninger for et bestemt mål. Sider under **Guider**. |
| `reference.md` | Referanse | Nøytral beskrivelse av et system, en ressurs eller et regelverk. Sider under **Referanse**. |
| `explanation.md` | Forklaring | Kontekst, bakgrunn og svar på «hvorfor?». Sider under **Om plattformen**. |

Hver mal bruker HTML-kommentarer (`<!-- OBLIGATORISK -->`, `<!-- VALGFRI: ... -->`) for å markere hvilke seksjoner som er påkrevde og hvilke som er en meny å velge fra. Kommentarene forklarer også _når_ hver valgfri seksjon er nyttig, med konkrete eksempler fra vår dokumentasjonsstruktur.

### Frontmatter

Malene bruker kun frontmatter-feltene som Zensical faktisk behandler:

| Felt | Påkrevd | Formål |
|------|---------|--------|
| `title` | Ja | Sidetittel |
| `description` | Ja | Norsk beskrivelse for søkemotorer |
| `diataxis` | Ja | Dokumentasjonstype (`tutorial`, `how-to`, `reference`, `explanation`) |
| `icon` | Nei | Overstyr sideikon (f.eks. `lucide/construction` for stub-sider) |

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

Skillen dekker det samme som skriveguidene i denne mappen, og laster inn riktig referansemateriale basert på hvilken dokumentasjonstype du jobber med. Malene (`tutorial.md`, `howto.md` osv.) er fortsatt nyttige som praktiske utgangspunkter selv om du har skillen installert — malene gir deg struktur, skillen gir AI-agenten din skjønn.
