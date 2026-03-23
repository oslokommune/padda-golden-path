# Skriveguide for dokumentasjon

Bruk denne sjekklisten når du skriver eller vurderer dokumentasjonssider. Den dekker kvalitetskriterier som gjelder på tvers av alle fire Diataxis-typer, med type-spesifikke huskelister til slutt.

For maler og strukturell veiledning, se:

| Fil | Type | Brukes til |
|-----|------|------------|
| [`tutorial.md`](tutorial.md) | Tutorial | Guidede læringsopplevelser. Sider under **Kom i gang**. |
| [`howto.md`](howto.md) | How-to | Oppgaverettede anvisninger. Sider under **Guider**. |
| [`explanation.md`](explanation.md) | Forklaring | Kontekst, bakgrunn og svar på "hvorfor?". Sider under **Om plattformen**. |
| [`reference.md`](reference.md) | Referanse | Nøytrale faktabeskrivelser. Sider under **Referanse**. |

Prinsippene bak de fire typene er beskrevet i [Diataxis-rammeverket](https://diataxis.fr/).


## Før du begynner å skrive

- [ ] **Hvilken type er dette?** Velg én: tutorial, how-to, forklaring eller referanse. Hvis svaret er "litt av begge", splitt siden.
- [ ] **Hvem er leseren?** Beslutningstaker, dataingeniør, analytiker eller nytt teammedlem? Dette påvirker ordvalg og antatt forkunnskapsnivå.
- [ ] **Hva sitter leseren igjen med?** Skriv én setning som beskriver utbyttet. Klarer du det ikke, mangler siden fokus.


## Skannbarhet

- [ ] **Leseren forstår hva siden handler om på 10 sekunder** — ut fra tittel, innledning og overskrifter alene.
- [ ] **Overskrifter beskriver innholdet** — "Konfigurer tilgangsnøkler" fremfor "Trinn 2".
- [ ] **Innledningen sier hva siden hjelper med** — ingen generisk velkomsttekst.
- [ ] **Lange sider har en tydelig struktur** — logiske seksjoner, ikke en vegg av tekst.


## Klarspråk

- [ ] **Korte, aktive setninger** — foretrekk "Kjør kommandoen" fremfor "Kommandoen kan kjøres av brukeren".
- [ ] **Ingen uforklart fagsjargong** — hvis et begrep ikke er allmennkunnskap for målgruppen, forklar det eller lenk til en forklaringsside.
- [ ] **Korrekt norsk** — bruk reelle norske ord, ikke anglisismer der gode norske alternativer finnes. Se [Språkrådets avløserord](https://www.sprakradet.no/sprakhjelp/Skriverad/Avloeysarord/).
- [ ] **Konsekvent terminologi** — bruk samme begrep for samme konsept gjennom hele siden og på tvers av dokumentasjonen.


## Fullstendighet

- [ ] **Forutsetninger er eksplisitte** — hva leseren trenger før start (tilganger, verktøy, tidligere steg).
- [ ] **Ingen manglende steg** — en leser som følger siden skal ikke måtte gjette hva som skjer mellom trinnene.
- [ ] **Verifikasjon finnes** — leseren vet om de lyktes ("du skal nå se X").
- [ ] **Lenker til relaterte sider** — tutorials lenker til how-tos, how-tos lenker til referanse, forklaringer lenker til begge.


## Formatering og Zensical-funksjoner

- [ ] **Kodeblokker har språkidentifikator** — ` ```python `, ikke bare ` ``` `.
- [ ] **Admonitions brukes etter formål** — `warning` for fare, `tip` for observasjoner, `note` for viktige merknader. Ikke for pynt.
- [ ] **Content tabs kun ved reelle varianter** — CLI vs. UI, Python vs. SQL. Ikke for sekvensielle steg.
- [ ] **Bilder ligger i samme mappe** som markdown-filen som refererer dem.
- [ ] **Ikke overdriv formatering** — fet skrift, kursiv og admonitions mister effekten ved overbruk.


## Frontmatter

- [ ] `title` — kort og beskrivende
- [ ] `description` — skrevet for søkemotorer, beskriver hva leseren får
- [ ] `diataxis` — én av: `tutorial`, `how-to`, `explanation`, `reference`
- [ ] `icon: lucide/construction` — kun på stub-sider (fjern når innholdet er skrevet)
- [ ] Ikke bruk `status: new` på stub-sider (gir dobbelt ikon sammen med `icon`)


---

## Type-spesifikke huskelister

Se malene for fullstendig struktur og eksempler.

### Tutorial → [`tutorial.md`](tutorial.md)

- [ ] Bruker "vi"-form gjennomgående ("Vi oppretter nå ...", ikke "Opprett ...")
- [ ] Én sti — ingen valg, ingen content tabs, ingen "alternativt"
- [ ] Hvert trinn gir et synlig resultat med "Forventet resultat"
- [ ] Avslutter med "Du har nå" som oppsummerer hva leseren har bygd
- [ ] Feilsøking i sammenleggbare `??? failure`-blokker (avbryter ikke den glade stien)

### How-to → [`howto.md`](howto.md)

- [ ] Oppgaverettet tittel ("Hvordan [oppnå X]")
- [ ] Antar kompetanse — lærer ikke bort grunnleggende ting
- [ ] Ingen bakgrunn eller teori — lenker ut i stedet
- [ ] Betinget veiledning der det finnes legitime varianter ("Hvis du bruker ...")
- [ ] Avslutter med "Bekreft resultatet" — et konkret verifikasjonssteg

### Forklaring → [`explanation.md`](explanation.md)

- [ ] Svarer på "hvorfor?", ikke "hvordan?"
- [ ] Ingen trinn-for-trinn-instruksjoner (de hører hjemme i tutorial eller how-to)
- [ ] Ingen parameterlister eller spesifikasjoner (de hører hjemme i referanse)
- [ ] Reflekterende, diskuterende tone — det er OK å resonnere og veie alternativer
- [ ] Lenker til relaterte tutorials, how-tos og referansesider

### Referanse → [`reference.md`](reference.md)

- [ ] Nøytral, saklig, objektiv — beskriver hva noe ER
- [ ] Strukturen speiler det som dokumenteres, ikke en brukerreise
- [ ] Komplett — dokumenterer alle tilfeller, ikke bare de vanlige
- [ ] Konsistent formatering innenfor siden og på tvers av søster-referansesider
- [ ] Korte eksempler for å illustrere, ikke for å lære bort
