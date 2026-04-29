---
title: Gjenopprette fra backup
description: Hvordan hente tilbake filer i landing zone og Databricks-tillatelser fra backup.
diataxis: how-to
icon: lucide/construction
---

# Gjenopprette fra backup

Denne veiledningen hjelper deg hente tilbake innhold fra S3-backupene som Golden Path tar av landing zone og Databricks-metadata (`system.information_schema`). Et vellykket resultat er at filene ligger i en ny eller eksisterende bøtte, og — hvis du gjenoppretter metadata — at tillatelsene er satt tilbake i Databricks.

For gjenoppretting etter feil i en pipeline-kjøring (rerun, checkpoints, schema-endringer), se [Gjenopprette etter feil i pipelines](gjenopprette-etter-feil.md).

## Før du begynner

Sørg for at du har:

- Tilgang til AWS-kontoen der backupen ligger, med rettigheter til å starte restore-jobber i AWS Backup
- Databricks workspace-admin hvis du skal gjenopprette tillatelser
- Navnet på bøtten eller backup-vaulten du vil gjenopprette fra, og tidspunkt/recovery point
- Python 3 lokalt hvis du skal konvertere metadata-backup til SQL

## Trinn 1: Finn riktig recovery point

1. Åpne **AWS Backup** i kontoen der backupen ligger.
2. Gå til **Backup vaults** og velg vaulten som inneholder backupen.
3. Finn recovery point for ønsket tidspunkt. Noter ID-en.

!!! note
Landing zone og metadata-bøtten er separate backup-kilder. Sjekk at du har valgt riktig vault for det du skal gjenopprette.

## Trinn 2: Velg en rolle som kan skrive til S3

Standardrollen for restore i AWS Backup har **ikke** rettigheter til S3. Bruk i stedet rollen som ble opprettet sammen med backup-jobben, og som har policyen `AWSBackupServiceRolePolicyForS3Restore`.

1. Gå til **IAM → Roles** i AWS-konsollen.
2. Søk etter roller med navn på formen `aws-backup-[dato][tall]`.
3. Noter ARN-en for rollen.

!!! warning
Hvis du kjører restore med standardrollen feiler jobben med en rettighetsfeil. Det er ingen automatisk fallback.

## Trinn 3: Start restore-jobben

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
