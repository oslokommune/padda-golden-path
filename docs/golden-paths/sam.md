# Bruk av lambdaer med SAM og GitHub Actions

For å hente inn informasjon fra kilder (altså pull i stedet for push) må et program utenfor Databricks hente dataen utenfra, og så skrive den til landing zone-området i S3. Deretter er det tilgjengelig fra Databricks for videre prosessering. Å hente data inn til landing zone gjøres ved hjelp av Lambda-funksjoner som kjører i en felles AWS-konto for alle. Disse konfigureres med SAM, og deployes via GitHub Actions. See `.github/workflows/deploy.yml` for et eksempel på hvordan det kan gjøres.

Fordi lambda-funksjonene kjører i en felles AWS-konto, er det strenge begrensninger på hva som kan gjøres med de. De lages i padda-iac-repoet, og deretter kan de modifiseres på svært begrenset vis. Stort sett er det kun koden og tidspunkter den kjøres på som kan endres.

Arbeidsflyt er altså følgende:

1. Opprett PR med ny lambda-funksjon i `padda-iac`-repoet. Her er det noen få variabler, men det viktigste er datakilde og sensitivitet. PRen har gjerne dummy-kode.
2. Når PR er godkjent blir denne deployet i AWS. Deretter kan den modifiseres med SAM. SAM kjøres ikke for hånd, men gjennom GitHub Actions.
