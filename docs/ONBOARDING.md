# Onboarding — Padda dataplattform

Velkommen til Padda, DIG sin dataplattform. Før du får tilgang til plattformen, ber vi deg lese gjennom og bekrefte at du har forstått retningslinjene nedenfor.

## Formål

Padda er Oslo kommunes dataplattform for datainnsamling, prosessering og analyse. Plattformen gjør det mulig for dataproduktteam å jobbe effektivt med data på en sikker og strukturert måte.

## Sjekkliste før bruk av Dataplattformen (Databricks)

**Dataeierskap og samtykke**
Du har ansvar for at dataeier har samtykket til opplasting og er kjent med risikoen ved bruk av plattformen.

**Risikovurdering (ROS)**
Det må gjennomføres en egen risikovurdering for bruk av dine data samt en personvernvurdering dersom det behandles personopplysninger. Risikovurdering av Databricks er beskrevet i [gjeldende ROS](https://oslokommune.sharepoint.com/:b:/r/sites/21b20/Felles-dokumenter/Dataspeilet/ROS%20Data%20engineering%20plattform/ROS-rapport%20Dataengineeringplattform%20med%20Databricks.pdf?csf=1&web=1&e=VxwG4d). Du må ha satt deg inn i dette før plattformen tas i bruk. Vi har utarbeidet mal for gjennomføring av en ROS-prosess som kan benyttes om ønskelig, som ligger [her](https://miro.com/app/board/uXjVGQbi2BY=/). Vi har også utarbeidet en mal for en ROS-rapport som kan benyttes, som ligger [her](https://oslokommune.sharepoint.com/:w:/r/sites/TEAM-DIG-JIPI/Delte%20dokumenter/General/ROS%20Metoder/ROS-NextGen/MAL%20Rosrapport%20Databricks%20dataproduktteam.docx?d=w3ceef0c9ba314bc595e458967e19342d&csf=1&web=1&e=lCahPa).

**Tilgangsstyring**
Du er ansvarlig for å forstå og velge riktig tilgangsnivå for datasettene dine.

**Ingen SLA**
Plattformen er under utvikling, og det foreligger per i dag ingen SLA knyttet til oppetid eller tilgjengelighet.

**Backup og redundans**
Du er selv ansvarlig for å sørge for redundant lagring av dataene.
Dataplattformen tar ikke backup av datasettene i løsningen.

# Onboarding — slik bekrefter du

For å få tilgang til Padda dataplattform må du bekrefte at du har lest og forstått retningslinjene våre. Dette gjør du ved å opprette en pull request (PR) direkte på GitHub.

## Steg for steg - GUI

1. **Les retningslinjene** ovenfor.

2. **Gå til mappen [`onboarding/brukere/`](https://github.com/oslokommune/padda-golden-path/tree/main/onboarding/brukere)** på GitHub.

3. **Klikk "Add file"** → **"Create new file"**.

4. **Gi filen navn** med ditt navn som filnavn, f.eks. `ola.nordmann.md`.

5. **Legg til følgende innhold** i editoren:
   ```markdown
   # Ola Nordmann
   - Dato: 2026-02-17
   - Jeg bekrefter at jeg har lest og forstått retningslinjene i ONBOARDING.md
   ```

6. **Klikk "Commit changes..."**, velg **"Create a new branch for this commit and start a pull request"**, og klikk **"Propose changes"**.

7. **Fyll ut PR-malen** — kryss av alle punktene i sjekklisten og fyll inn navn og dato. Klikk **"Create pull request"**.

## Steg for steg - IDE

1. **Les retningslinjene** ovenfor.

2. **Hent repoet til din maskin**
    ```bash
    git clone https://github.com/oslokommune/padda-golden-path.git
    ```
3. **Opprett en ny branch** fra `main`:
   ```bash
   git checkout main && git pull
   git checkout -b onboarding/ditt.navn
   ```
4. **Lag en fil** i `onboarding/brukere/` med ditt navn som filnavn, f.eks. `ola.nordmann.md`:
   ```bash
   touch onboarding/brukere/ola.nordmann.md
   ```
5. **Legg til følgende innhold** i filen:
   ```markdown
   # Ola Nordmann
   - Dato: 2026-02-17
   - Jeg bekrefter at jeg har lest og forstått retningslinjene i ONBOARDING.md
   ```
6. **Commit og push**:
   ```bash
   git add onboarding/brukere/ola.nordmann.md
   git commit -m "onboarding: ola nordmann"
   git push -u origin onboarding/ditt.navn
   ```
7. **Opprett en PR** mot `main`-branchen og be om review fra team dataspeilet.
## Hvorfor denne prosessen?

- Skaper en sporbar logg over hvem som har lest og godtatt retningslinjene.


## Kontakt

Har du spørsmål eller trenger hjelp? Ta kontakt via:

- **Slack**: [#dig-dataspeilet](https://oslokommune.slack.com/archives/C01SFNFEXK7)
- **GitHub**: [oslokommune/padda-golden-path](https://github.com/oslokommune/padda-golden-path) — opprett et issue eller ta kontakt via PR
