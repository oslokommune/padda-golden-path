# Onboarding — Padda dataplattform

Velkommen til Padda, DIG sin dataplattform. Før du får tilgang til plattformen, ber vi deg lese gjennom og bekrefte at du har forstått retningslinjene nedenfor.

## Formål

Padda er Oslo kommunes dataplattform for datainnsamling, prosessering og analyse. Plattformen gjør det mulig for dataproduktteam å jobbe effektivt med data på en sikker og strukturert måte.

## Sjekkliste før bruk av Dataplattformen (Databricks)

1. Dataeierskap og samtykke
Du har ansvar for at dataeier har samtykket til opplasting og er kjent med risikoen ved bruk av plattformen.

2. Risikovurdering (ROS)
Det må gjennomføres en egen risikovurdering for bruk av dine data. Vi har utarbeidet mal for gjennomføring av en ROS-prosess som kan benyttes om ønskelig, som ligger her.
Vi har også utarbeidet en mal for en ROS-rapport som kan benyttes, som ligger her.
Risikovurdering av Databrikcs er beskrevet i gjeldende ROS.
Du må ha satt deg inn i dette før plattformen tas i bruk. 

3. Tilgangsstyring
Du er ansvarlig for å forstå og velge riktig tilgangsnivå for datasettene dine.

4. Ingen SLA
Plattformen er under utvikling, og det foreligger per i dag ingen SLA knyttet til oppetid eller tilgjengelighet.

5. Backup og redundans
Du er selv ansvarlig for å sørge for redundant lagring av dataene.
Dataplattformen tar ikke backup av datasettene i løsningen.

# Onboarding — slik bekrefter du

For å få tilgang til Padda dataplattform må du bekrefte at du har lest og forstått retningslinjene våre. Dette gjør du ved å opprette en pull request (PR) til https://github.com/oslokommune/padda-golden-path

## Steg for steg

1. **Les retningslinjene** ovenfor.
2. **Opprett en ny branch** fra `main`:
   ```bash
   git checkout main && git pull
   git checkout -b onboarding/ditt.navn
   ```
3. **Lag en fil** i `onboarding/brukere/` med ditt navn som filnavn, f.eks. `ola.nordmann.md`:
   ```bash
   touch onboarding/brukere/ola.nordmann.md
   ```
4. **Legg til følgende innhold** i filen:
   ```markdown
   # Ola Nordmann
   - Dato: 2026-02-17
   - Jeg bekrefter at jeg har lest og forstått retningslinjene i ONBOARDING.md
   ```
5. **Commit og push**:
   ```bash
   git add onboarding/brukere/ola.nordmann.md
   git commit -m "onboarding: ola nordmann"
   git push -u origin onboarding/ditt.navn
   ```
6. **Opprett en PR** mot `main`-branchen og be om review fra team dataspeilet.

## Hvorfor denne prosessen?

- Skaper en sporbar logg over hvem som har lest og godtatt retningslinjene.


## Kontakt

Har du spørsmål eller trenger hjelp? Ta kontakt via:

- **Slack**: [#dig-dataplattform](https://oslokommune.slack.com/archives/C01SFNFEXK7)
- **GitHub**: [oslokommune/padda-golden-path](https://github.com/oslokommune/padda-golden-path) — opprett et issue eller ta kontakt via PR
