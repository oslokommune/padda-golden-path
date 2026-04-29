---
title: Gjenopprette når uhellet er ute
description: Hvordan komme seg tilbake til et fungerende system.
diataxis: how-to
icon: lucide/construction
---

# Gjenopprette når uhellet er ute

Denne veiledningen hjelper deg når ting har gått galt og viktig data er mistet.

For gjenoppretting etter feil i en pipeline-kjøring (rerun, checkpoints, schema-endringer), se [Gjenopprette etter feil i pipelines](gjenopprette-etter-feil.md).

## Før du begynner

Hva du trenger kommer helt an på hvor galt det har gått. I verste fall er det eneste du trenger mulighet til å nå AWS- og Databricks-support. Vi forutsetter at nåde-perioden for sletting av AWS- og Databricks-kontoer ikke er utløpt.

Finn ut hva som har skjedd og hopp til det steget. Forhåpentligvis er ikke alt her relevant.

## Trinn 1: Sørg for at Databricks og AWS er satt opp riktig

Skulle dette ikke være på plass er den enkleste måten å komme tilbake på å kontakte AWS og Databricks og be om gjenoppretting av kontoer. Naturligvis først AWS-kontoer (dev og prod) og deretter de to tilhørende Databricks-kontoene.

Vi bruker [IaC](https://github.com/oslokommune/padda-iac) og de overordnede strukturene er der. Hvis AWS- eller Databricks-konto er ikke kan gjenopprettes så kan det kreve litt tilpassing av variabler som Databricks-kontonummer. Den som gjenoppretter må sikre seg admin-rettigheter for Databricks og AWS og kjøre (`terraform apply`) alle Terraform-stackene der.

## Trinn 2: Gjenopprett kode i eventuelt rammede workspacer

Kode som kjører i et workspace skal ligge under versjonskontroll. [Her er SYE-koden](https://github.com/oslokommune/sye-dvh-dataplattform) som eksempel. Alle DABer, AWS Lambdaer og annen programvare der må settes opp.

Sjekk README i det gjeldende prosjektet for mer info om hvordan dette gjøres.

## Trinn 3: Gjenopprett landing zone der nødvendig

Data i landing zone kan gjenopprettes med AWS Backup om nødvendig.

### Trinn 1: TODO

### Trinn 2: Velg en rolle som kan skrive til S3

Standardrollen for restore i AWS Backup har **ikke** rettigheter til S3. Bruk i stedet rollen som ble opprettet sammen med backup-jobben, og som har policyen `AWSBackupServiceRolePolicyForS3Restore`.

1. Gå til **IAM → Roles** i AWS-konsollen.
2. Søk etter roller med navn på formen `aws-backup-[dato][tall]`.
3. Noter ARN-en for rollen.

!!! warning
Hvis du kjører restore med standardrollen feiler jobben med en rettighetsfeil. Det er ingen automatisk fallback.

### Trinn 3: Start restore-jobben

1. I **AWS Backup**, velg recovery point fra trinn 1 og klikk **Restore**.
2. Velg destinasjonsbøtte (ny eller eksisterende).
3. Under **IAM role**, velg rollen fra trinn 2.
4. Start jobben og vent til status er **Completed**.

!!! warning
Hvis du gjenoppretter til en eksisterende bøtte, vil filer med samme navn kunne bli overskrevet. Vurder å gjenopprette til en ny bøtte først og kopiere over manuelt.

[TODO: verifisere eksakte menyvalg i AWS Backup-konsollen og legge inn CLI-alternativ hvis relevant.]

## Trinn 4: Gjenopprett Databricks-tillatelser

Gjør dette bare hvis du har gjenopprettet metadata-backupen (JSON-filer fra `system.information_schema`).

1. Last ned JSON-filene fra den gjenopprettede bøtten til en lokal mappe.
2. Kjør konverteringsscriptet for å generere SQL:

   ```bash
   python scripts/restore/generate_privilege_sql.py <mappe-med-json>
   ```

   Scriptet skriver `GRANT`-setninger for kataloger, skjemaer, tabeller og volumer til stdout.

3. Inspiser SQL-utdataet og lagre det til fil:

   ```bash
   python scripts/restore/generate_privilege_sql.py ./restore-json > privileges.sql
   ```

4. Kjør SQL-filen i Databricks (SQL Editor eller via en notebook tilknyttet et workspace der du er admin).

!!! note
Scriptet gjenoppretter bare tillatelser som ikke er arvet (`inherited_from = NONE`). Arvede tillatelser følger automatisk når foreldreobjektets tillatelser er på plass.

## Bekreft resultatet

For landing zone-restore:

```bash
aws s3 ls s3://<destinasjonsbøtte>/ --recursive | head
```

Kontroller at forventede filer og prefikser er til stede.

For tillatelses-restore, kjør i Databricks:

```sql
SHOW GRANTS ON CATALOG <katalognavn>;
```

Forventet utdata: Tillatelsene du forventer å ha gjenopprettet, listet med `principal`, `action_type` og `object_type`.

## Feilsøking

??? failure "Restore-jobb feiler med `AccessDenied` mot S3"
Sannsynlig årsak: Du brukte standardrollen for AWS Backup, som ikke har `AWSBackupServiceRolePolicyForS3Restore`.

    Løsning:

    - Start jobben på nytt med rollen `aws-backup-[dato][tall]` (se trinn 2).

??? failure "`generate_privilege_sql.py` feiler med `<filnavn>.json not found`"
Sannsynlig årsak: Mappen du pekte på mangler én eller flere av de forventede filene (`catalog_privileges.json`, `schema_privileges.json`, `table_privileges.json`, `volume_privileges.json`).

    Løsning:

    - Kontroller at restore-jobben faktisk fullførte og at alle objekttyper er med i backupen.
    - Hvis en objekttype bevisst mangler i denne backupen, kjør scriptet mot en undermappe som inneholder filene som finnes.

??? failure "`GRANT`-setningen feiler i Databricks med `principal does not exist`"
Sannsynlig årsak: Gruppen eller brukeren som hadde tilgang er slettet eller endret siden backupen ble tatt.

    Løsning:

    - Verifiser principalen i workspace-admin og tilpass SQL-en før du kjører den.

## Relatert innhold

- [Backup](../../om-plattformen/konsepter/backup.md) — hvorfor backup er satt opp slik den er
- [Gjenopprette etter feil i pipelines](gjenopprette-etter-feil.md)
- [`scripts/restore/generate_privilege_sql.py`](../../../scripts/restore/generate_privilege_sql.py)
