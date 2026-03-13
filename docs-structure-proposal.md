# Forslag til dokumentasjonsstruktur for Padda

## Hvem er dette forslaget for?

Dette forslaget beskriver en ny dokumentasjonsstruktur for Padda — Databricks-basert
dataplattform bygget av Digitaliseringsetaten (DIG) for Oslo kommune.

Brukerne våre er **data engineers og analytikere** i kommunens etater og bydeler.
De skriver kode (Python, SQL, R), bygger og eier sine egne pipelines, og trenger
tydelig, oppgaveorientert dokumentasjon for å være produktive på plattformen.

**Beslutningstagere** trenger også å raskt forstå hva plattformen tilbyr og om den
passer — uten salgsspråk.

Dette er **ikke** dokumentasjonsportalen for Fabric. Vi nevner Fabric kun for å
hjelpe brukere som havner her ved en feil, og for å dokumentere konkrete
integrasjoner (hente data fra Fabric, dele data med Fabric).

---

## Strukturen i fugleperspektiv

```
Forside
├── Om plattformen
├── Kom i gang
├── Hente inn data
├── Bearbeide data
├── Dele og hente ut data
├── Overvåke og drifte
└── Hjelp
```

Sju hoveddeler, organisert rundt **brukerens reise** og **arbeidsflyt** — ikke
rundt vår interne teamstruktur.

---

## Designprinsipper

### Brukerens reise kommer først

Strukturen følger veien en bruker tar fra oppdagelse til daglig arbeid:

| Fase                      | Seksjon                              | Brukerens spørsmål                         |
| ------------------------- | ------------------------------------ | ------------------------------------------ |
| Oppdagelse og vurdering   | Om plattformen                       | «Er dette riktig plattform for meg?»       |
| Onboarding                | Kom i gang                           | «Hvordan kommer jeg i gang?»               |
| Daglig arbeid             | Hente inn / Bearbeide / Dele         | «Hvordan gjør jeg X?»                      |
| Drift                     | Overvåke og drifte                   | «Hvordan holder jeg pipelinene friske?»    |
| Løpende støtte            | Hjelp                                | «Jeg sitter fast — hvor går jeg?»          |

### Pipeline-faser strukturerer det daglige arbeidet

Når brukeren er forbi onboarding, tenker de i dataflyten sin: hente inn,
bearbeide, dele. Disse tre fasene blir hovednavigasjonen for
arbeidsdokumentasjonen, fremfor å organisere etter Diataxis-type.

### Diataxis lever inni hver seksjon, ikke på toppen

Vi bruker de fire Diataxis-typene — Tutorial (T), How-to (H), Explanation (E)
og Reference (R) — som innholdstyper innenfor hver seksjon. Typene styrer
*hva slags side man skriver*, men de driver ikke toppnivå-navigasjonen.

Titler signaliserer typen naturlig:

- «Om ...» = Explanation
- «Sette opp ...» / «Laste opp ...» = How-to
- «Din første ...» = Tutorial
- «Referanse: ...» = Reference

### Bare brukerrettet innhold hører hjemme her

Hvis en side primært hjelper plattformteamet med å utvikle eller drifte
plattformen, hører den hjemme i intern dokumentasjon — ikke her. Testen:
*hjelper denne siden en bruker av plattformen med å gjøre jobben sin?*

---

## Detaljert struktur

### Forside

Forsiden orienterer og dirigerer. Den svarer på tre spørsmål:

- Hva er Padda? (én setning)
- Hvem er det for? (målgruppe)
- Hvor skal jeg gå? (veivisere til seksjoner)

Den avklarer også: *«Denne dokumentasjonen dekker Databricks-plattformen (Padda).
Leter du etter Fabric-dokumentasjon? Kontakt [team/kanal].»*

### Om plattformen

For beslutningstagere og nye brukere som vurderer plattformen.

| Side                                         | Type | Beskrivelse                                              |
| -------------------------------------------- | ---- | -------------------------------------------------------- |
| Hva tilbyr dataplattformen                   | E    | Verdiforslag: hva Padda gjør, hvem det er for            |
| Er Databricks-plattformen riktig for deg?    | E    | Forutsetninger: dataegnethet, nødvendig kompetanse, behov |
| Arkitektur                                   | E    | Medallion-arkitektur, hovedkomponenter, dataflyt         |
| Bruksområder                                 | E    | Konkrete brukseksempler fra virksomheter                 |
| Brukervilkår og ditt ansvar                  | R    | Dataeierskap, SLA, backup, ansvarsfordeling              |

### Kom i gang

For nye brukere som skal gå fra «jeg har en konto» til «jeg har en fungerende
pipeline». Seksjonen dekker både testfasen og veien til produksjon.

| Side                          | Type | Beskrivelse                                          |
| ----------------------------- | ---- | ---------------------------------------------------- |
| Oversikt og sjekkliste        | —    | Kart over læringsløpet, sjekkliste for ansvar        |
| Konto og tilgang              | H    | Hvordan få tilgang, roller, rettigheter, testmiljø   |
| Sett opp utviklingsmiljøet    | H    | Installere verktøy, konfigurere CLI og IDE           |
| Din første datapipeline       | T    | Tutorial fra ende til ende: hente inn, bearbeide, dele |
| VS Code og Databricks         | T    | Tutorial: lokal utvikling med VS Code-utvidelsen     |
| Testdata                      | H    | Hva slags data kan brukes i test, syntetiske data, anonymisering |
| Fra test til produksjon       | H    | Krav til proddata: dataminimering, rettslig grunnlag, formål |
| Læringsressurser              | —    | Databricks-kurs, videoer, lesetips                   |

### Hente inn data

For brukere som skal få data inn i plattformen.

| Side                                  | Type | Beskrivelse                                      |
| ------------------------------------- | ---- | ------------------------------------------------ |
| Om datainnlasting                     | E    | Innlastingsstrategier, formater, dataklassifisering (grønn/gul/rød) |
| Laste opp filer til landing zone      | H    | Laste opp filer via S3, IAM-oppsett              |
| Laste inn Excel til Unity Catalog     | H    | Excel til Delta-tabell via DAB                   |
| Hente data fra API med Lambda         | H    | SAM-template, Lambda-handler, scheduling         |
| Hente data fra Fabric                 | H    | Hente data fra Fabric inn i Databricks           |
| Sette opp Auto Loader                 | H    | Inkrementell filinnlasting                       |
| Håndtere secrets                      | H    | Secret scopes, lagring av credentials            |
| Referanse: Landing zone               | R    | Struktur, IAM-roller, tilgangsmodell, filformater |

### Bearbeide data

For brukere som transformerer rådata til forretningsklare datasett.

| Side                              | Type | Beskrivelse                                      |
| --------------------------------- | ---- | ------------------------------------------------ |
| Om medallion-arkitekturen         | E    | Hvorfor bronze/silver/gold, designvalg           |
| Skrive transformasjoner           | H    | Jobbe med notebooks og jobber                    |
| Bronze til silver                 | H    | Rensing, deduplisering, standardisering          |
| Silver til gold                   | H    | Aggregering, forretningslogikk                   |
| Laste opp Python-biblioteker     | H    | Laste opp wheel-filer til UC Volume for bruk offline |
| Referanse: Navnekonvensjoner      | R    | Standarder for tabell- og skjemanavn             |

### Dele og hente ut data

For brukere som gjør data tilgjengelig for konsumenter.

| Side                                  | Type | Beskrivelse                                  |
| ------------------------------------- | ---- | -------------------------------------------- |
| Om datatilgang og deling              | E    | Delingsstrategier, tilgangskontrollkonsepter |
| Koble Power BI til SQL Warehouse      | H    | Koble Power BI til Databricks                |
| Dele data via Unity Catalog           | H    | Deling på tvers av workspaces og kataloger   |
| Dele data med Fabric                  | H    | Sende data fra Databricks til Fabric         |
| Referanse: SQL Warehouse              | R    | Konfigurasjon, tilkoblingsdetaljer           |

### Overvåke og drifte

For brukere som eier pipelines i produksjon. *You build it, you run it* —
plattformen gjør det enkelt, men ansvaret er ditt.

| Side                                               | Type | Beskrivelse                              |
| -------------------------------------------------- | ---- | ---------------------------------------- |
| Om overvåking av pipelines                         | E    | Hva plattformen tilbyr, hva du eier      |
| Sette opp Slack-alarmer                            | H    | Notification destinations, varsling      |
| Feilhåndtering i pipelines                         | H    | Vanlige feilsituasjoner, gjenoppretting  |
| Logging                                            | H    | Hvor du finner logger, hvordan bruke dem |
| Referanse: Varsling og notification destinations   | R    | Tilgjengelige kanaler, konfigurasjon     |

### Hjelp

For aktive brukere som trenger støtte.

| Side          | Type | Beskrivelse                                      |
| ------------- | ---- | ------------------------------------------------ |
| FAQ           | —    | Ofte stilte spørsmål                             |
| Kontakt oss   | —    | Hvem du kontakter, hvilken kanal for hva         |
| Fellesskap    | —    | Kunnskapsdeling, møteplasser                     |
| Kurs          | —    | Tilgjengelig opplæring (tilgangsstyring, personvern) |
| Nyheter       | —    | Endringslogg, kunngjøringer                      |

---

## Kartlegging av eksisterende innhold

### Innhold som flyttes inn i ny struktur

| Eksisterende fil                           | Ny plassering                        | Hva som må gjøres    |
| ------------------------------------------ | ------------------------------------ | -------------------- |
| `index.md`                                 | Forside                              | Skrives helt om      |
| `getting-started.md`                       | Kom i gang / Din første datapipeline | Strammes opp som ren tutorial |
| `ONBOARDING.md`                            | Om plattformen / Brukervilkår og ditt ansvar | Skrives om: fokus på vilkår og ansvar, ikke PR-prosess |
| `guides/developer/dev-setup.md`            | Kom i gang / Sett opp utviklingsmiljøet | Flyttes, mindre justeringer |
| `vscode-demo/1-4.md`                       | Kom i gang / VS Code og Databricks   | Slås sammen til én tutorial |
| `guides/data/landing-zone.md`              | Splittes i to sider                  | How-to-del → Hente inn data / Laste opp filer. Referanse-del → Hente inn data / Referanse: Landing zone |
| `guides/data/laste-opp-excel-til-uc.md`    | Hente inn data / Laste inn Excel     | Flyttes              |
| `guides/developer/lambda-api.md`           | Hente inn data / Hente data fra API  | Flyttes              |
| `guides/developer/secrets.md`              | Hente inn data / Håndtere secrets    | Flyttes              |
| `guides/developer/laste-opp-lib.md`        | Bearbeide data / Laste opp Python-biblioteker | Flyttes     |
| `guides/developer/slack-alarmer.md`        | Overvåke og drifte / Sette opp Slack-alarmer | Flyttes, utvides |
| `notion/arkitektur-wip.md`                 | Om plattformen / Arkitektur + Bearbeide data / Om medallion-arkitekturen | Skrives om og splittes |
| `notion/tilgangsstyring-og-roller.md`      | Kom i gang / Konto og tilgang        | Skrives om           |
| `guides/roller/*.md` (5 filer)             | Kom i gang / Konto og tilgang        | Samles til én rolle-/rettighetsoversikt innenfor siden |

### Innhold som ikke hører hjemme i offentlig dokumentasjon

| Eksisterende fil                           | Begrunnelse                                      |
| ------------------------------------------ | ------------------------------------------------ |
| `architecture/dataflyt_sye.md`             | Virksomhetsspesifikk dataflyt, sikkerhetsrisiko  |
| `notion/github-struktur-iac-dab-ci-cd.md`  | Intern repo-struktur, ikke brukerrettet          |
| `architecture/progresjon.md`               | Internt veikart (kan evt. bli «Om plattformen / Veikart» hvis ønskelig) |

### Navigasjons- og indekssider som erstattes av ny struktur

| Eksisterende fil       | Skjebne               |
| ---------------------- | ---------------------- |
| `guides/index.md`      | Erstattes              |
| `notion/index.md`      | Erstattes              |

---

## Hva som mangler — per seksjon

Oversikt over nytt innhold som må skrives.

| Seksjon               | Nye sider | Diataxis-hull                                 |
| --------------------- | --------- | --------------------------------------------- |
| Om plattformen        | 3 av 5    | Nesten utelukkende Explanation — det største innholdshullet |
| Kom i gang            | 4 av 8    | Onboarding-guider, testdata, test→prod        |
| Hente inn data        | 2 av 8    | Fabric-integrasjon, Auto Loader               |
| Bearbeide data        | 4 av 6    | **Tynneste seksjonen** — transformasjon er kjerneaktiviteten men knapt dokumentert |
| Dele og hente ut data | 4 av 5    | Nesten helt manglende                         |
| Overvåke og drifte    | 4 av 5    | Nesten helt manglende                         |
| Hjelp                 | 5 av 5    | Helt manglende                                |

**Totalt: 13 eksisterende sider passer inn i strukturen. 28 nye sider må skrives.**

### Forslag til prioritering

1. **Om plattformen** — fjerner blokkering for nye brukere og beslutningstagere
2. **Bearbeide data** — kjerneaktiviteten, nesten udokumentert
3. **Dele og hente ut data** — hele poenget med plattformen
4. **Overvåke og drifte** — trengs når brukerne går i produksjon
5. **Hjelp** — kan starte med bare FAQ og kontaktinfo

---

## Diataxis-balanse

| Type             | Antall | Andel |
| ---------------- | ------ | ----- |
| Tutorial (T)     | 2      | 5 %   |
| How-to (H)       | 19     | 46 %  |
| Explanation (E)  | 9      | 22 %  |
| Reference (R)    | 6      | 15 %  |
| Annet            | 5      | 12 %  |

How-to dominerer, noe som er forventet for en plattform rettet mot praktikere.
Explanation-hullet er det viktigste å tette — uten det kan brukerne følge
instruksjoner, men forstår ikke *hvorfor*, og blir avhengige av support så
fort noe avviker fra den gylne stien.
