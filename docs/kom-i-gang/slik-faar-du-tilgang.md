---
title: Slik får du tilgang
description: Hvordan komme i gang med dataplattformen — brukervilkår, onboarding og innlogging.
diataxis: tutorial
---

# Slik får du tilgang

!!! info "Opprinnelse"
    Denne siden inneholder tutorial-delen fra `docs/ONBOARDING.md` og `docs/notion/tilgangsstyring-og-roller.md`. Brukervilkårene (referanse) ligger under [Brukervilkår og ansvar](../referanse/brukervilkaar.md). Roller og rettigheter (referanse) ligger under [Roller og rettigheter](../referanse/roller-og-rettigheter.md).

Bør dekke:

1. **Kontakt Team Dataspeilet** via [#dig-dataspeilet](https://oslokommune.slack.com/archives/C01SFNFEXK7) — oppgi formål, dataeierskap og teaminfo
2. **Hva skjer videre?** — onboarding-løpet etter at du har tatt kontakt
3. **Aksepter brukervilkår** — les brukervilkårene og bekreft via PR (se under)

## Aksepter brukervilkår via PR

For å få tilgang til Padda dataplattform må du bekrefte at du har lest og forstått [brukervilkårene](../referanse/brukervilkaar.md). Dette gjør du ved å opprette en pull request (PR) direkte på GitHub.

### Steg for steg - GUI

1. **Les retningslinjene** i [Brukervilkår og ansvar](../referanse/brukervilkaar.md).

2. **Gå til mappen [`onboarding/brukere/`](https://github.com/oslokommune/padda-golden-path/tree/main/onboarding/brukere)** på GitHub.

3. **Klikk "Add file"** → **"Create new file"**.

4. **Gi filen navn** med ditt navn som filnavn, f.eks. `ola.nordmann.md`.

5. **Legg til følgende innhold** i editoren:
   ```markdown
   # Ola Nordmann
   - Dato: 2026-02-17
   - Jeg bekrefter at jeg har lest og forstått [brukervilkårene for Padda dataplattform](../../docs/referanse/brukervilkaar.md)
   ```

6. **Klikk "Commit changes..."**, velg **"Create a new branch for this commit and start a pull request"**, og klikk **"Propose changes"**.

7. **Fyll ut PR-malen** — kryss av alle punktene i sjekklisten og fyll inn navn og dato. Klikk **"Create pull request"**.

### Steg for steg - IDE

1. **Les retningslinjene** i [Brukervilkår og ansvar](../referanse/brukervilkaar.md).

2. **Hent repoet til din maskin**
    ```bash
    git clone git@github.com:oslokommune/padda-golden-path.git
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
   - Jeg bekrefter at jeg har lest og forstått [brukervilkårene for Padda dataplattform](../../docs/referanse/brukervilkaar.md)
   ```
6. **Commit og push**:
   ```bash
   git add onboarding/brukere/ola.nordmann.md
   git commit -m "onboarding: ola nordmann"
   git push -u origin onboarding/ditt.navn
   ```
7. **Opprett en PR** mot `main`-branchen og be om review fra team dataspeilet.

### Hvorfor denne prosessen?

- Skaper en sporbar logg over hvem som har lest og godtatt retningslinjene.

## Logg inn

Databricks er konfigurert med Entra ID som Identity Provider. Brukere:

- logger på via SAML/SCIM SSO uten egne Databricks-passord
- får automatisk MFA-policy fra Entra ID
- opplever sømløs bytte mellom Workspaces fordi token kommer fra samme SSO

## Forstå flyten

Teknisk flyt:

1. **Entra ID** forvalter brukere, sikkerhetsgrupper og service-principals.
2. Grupper synkroniseres til Databricks via SCIM.
3. Ved pålogging bruker vi **SSO (SAML/SCIM)** slik at brukeren autentiseres en gang og får token i både konto og arbeidsområde.
4. Databricks workspace mapper gruppene til Unity Catalog-roller og til workspace-/job-ACL-er.
5. Unity Catalog kontrollerer sluttbrukerens tilgang til databaser, tabeller, volum og katalogmetadata.

## Sjekk din rolle

Se [Roller og rettigheter](../referanse/roller-og-rettigheter.md) for detaljer om hva du har tilgang til.
