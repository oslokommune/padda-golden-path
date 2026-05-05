---
title: Gjenopprette når uhellet er ute
description: Hvordan komme seg tilbake til et fungerende system.
diataxis: how-to
---

# Gjenopprette når uhellet er ute

Denne veiledningen hjelper deg når ting har gått galt og viktig data er mistet. Vi tar ikke backup av alt, så det du skal ende opp med er ikke en fullstendig gjenoppretting, men i stedet et fungerende system.

For gjenoppretting etter feil i en pipeline-kjøring (rerun, checkpoints, schema-endringer), se [Gjenopprette etter feil i pipelines](gjenopprette-etter-feil.md).

## Før du begynner

Hva du trenger kommer helt an på hvor galt det har gått. I verste fall er det eneste du trenger mulighet til å nå AWS- og Databricks-support, samt tilgang til IaC-repos på GitHub. Vi forutsetter at nåde-perioden for sletting av AWS- og Databricks-kontoer ikke er utløpt.

Finn ut hva som har skjedd og hopp til det steget. Forhåpentligvis er ikke alt her relevant.

## Trinn 1: Sørg for at Databricks og AWS er satt opp riktig

Skulle dette ikke være på plass er den enkleste måten å komme tilbake på å kontakte AWS og Databricks og be om gjenoppretting av kontoer. Naturligvis først AWS-kontoer (dev og prod) og deretter de to tilhørende Databricks-kontoene. Utviklerflyt-avdelingen og arkitektene i avdelingen for teknologi og sikker utvikling kan hjelpe med dette.

Vi bruker [IaC](https://github.com/oslokommune/padda-iac), og de overordnede strukturene er der. Hvis AWS- eller Databricks-konto ikke kan gjenopprettes så kan det kreve litt tilpassing av variabler som Databricks-kontonummer. Den som gjenoppretter må sikre seg admin-rettigheter for Databricks og AWS og kjøre `terraform apply` på alle Terraform-stackene der.

## Trinn 2: Gjenopprett kode i eventuelt rammede workspacer

Kode som kjører i et workspace skal ligge under versjonskontroll. [Her er SYE-koden](https://github.com/oslokommune/sye-dvh-dataplattform) som eksempel. Alle DABer, AWS Lambdaer og annen programvare der må settes opp.

Sjekk README i det gjeldende prosjektet for mer info om hvordan dette gjøres.

## Trinn 3: Gjenopprett landing zone der nødvendig

Data i landing zone kan gjenopprettes med AWS Backup om nødvendig. Landing zonen er en S3-bøtte med workspace-navn og "landing-zone" i navnet. Det relevante recovery point har et lignende navn.

### Trinn A: Velg en rolle som kan skrive til S3

Standardrollen for restore i AWS Backup har **ikke** rettigheter til S3. Bruk i stedet rollen som ble opprettet sammen med backup-jobben, og som har policyen `AWSBackupServiceRolePolicyForS3Restore`.

1. Gå til **IAM → Roles** i AWS-konsollen.
2. Søk etter roller med navn på formen `aws-backup-[dato][tall]`.
3. Noter ARN-en for rollen.

!!! warning
Hvis du kjører restore med standardrollen feiler jobben med en rettighetsfeil. Det er ingen automatisk fallback.

### Trinn B: Start restore-jobben

1. I **AWS Backup**, velg vault og recovery point, og klikk **Restore**.
2. Velg destinasjonsbøtte (ny eller eksisterende).
3. Under **Restore role**, velg rollen fra trinn 2.
4. Start jobben og vent til status er **Completed**.

!!! warning
Hvis du gjenoppretter til en eksisterende bøtte, vil filer i mål-bøtten med samme navn som i backup [ha prioritet](https://docs.aws.amazon.com/aws-backup/latest/devguide/restoring-s3.html#s3-restore-considerations). Hvis du ikke er sikker på at mål-bøtten er tom og at ingen skriver til den før restore er ferdig, vurder å gjenopprette til en ny bøtte først og kopiere over manuelt.

## Trinn 4: Kjør alle jobber og pipelines

Gå inn i Databricks og kjør alle jobber under "Jobs & Pipelines" slik de normalt sett hadde blitt kjørt automatisk. Dette betyr i praksis å kjøre alle jobber som har en schedule. Hvis det er noen continuous pipelines som er avslått så må disse også startes.

Dette burde bringe alle tabeller, etc. tilbake til det samme innhold de hadde før ting gikk galt. Sjekk et par tabeller manuelt og kontroller at ingenting er åpenbart feil.

## Trinn 5: Gjenopprett Databricks-tillatelser

!!! note
Sørg for at trinn 4 er gjort. Gjenoppretting av tillatelser på tabeller som ikke finnes vil fungere dårlig.

### Trinn A: Gjenopprett metadata-bøtten

Først må du gjenopprette metadata-backupen (JSON-filer fra `system.information_schema`). Se etter et recovery point med et navn som innneholder workspace-navnet og "information-schema-dump". Følg ellers stegene i trinn 3.

### Trinn B: Generer og kjør SQL-script

1. Last ned JSON-filene fra den gjenopprettede bøtten til en lokal mappe.
2. Kjør konverteringsscriptet for å generere SQL:

   ```bash
   python scripts/restore/generate_privilege_sql.py mappe_med_json > privileges.sql
   ```

   Scriptet skriver `GRANT`-setninger for kataloger, skjemaer, tabeller og volumer til stdout. Har du ikke Python lokalt kan det kjøres i Databricks.

3. Inspiser SQL-utdataet og fjern ting du ikke vil ha

4. Kjør SQL-filen i Databricks (SQL Editor eller via en notebook tilknyttet et workspace der du er admin).

!!! note
Scriptet gjenoppretter bare tillatelser som ikke er arvet (`inherited_from = NONE`). Arvede tillatelser følger automatisk når foreldreobjektets tillatelser er på plass.

## Bekreft resultatet

For landing zone-restore:

Kontroller at filer og prefikser ser noenlunde riktig ut i AWS-konsollen/GUI.

For tillatelses-restore, kjør i Databricks:

```sql
SHOW GRANTS ON CATALOG <katalognavn>;
```

Forventet utdata: Tillatelsene du forventer å ha gjenopprettet, listet med `principal`, `action_type` og `object_type`. Det bekrefter ikke alt, men burde være avslørende dersom ingenting fungerte.

Gå gjennom Databricks-UI og sjekk at jobber og pipelines går som normalt. Sjekk relevante Slack-kanaler for alerts. Sjekk at dashboards og Power BI-rapporter har plausible data.

## Feilsøking

??? failure "Restore-jobb feiler med `AccessDenied` mot S3"
Sannsynlig årsak: Du brukte standardrollen for AWS Backup, som ikke har `AWSBackupServiceRolePolicyForS3Restore`.

    Løsning:

    - Start jobben på nytt med rollen `aws-backup-[dato][tall]` (se trinn 3A).

??? failure "`generate_privilege_sql.py` feiler med `<filnavn>.json not found`"
Sannsynlig årsak: Mappen du pekte på mangler én eller flere av de forventede filene (`catalog_privileges.json`, `schema_privileges.json`, `table_privileges.json`, `volume_privileges.json`).

    Løsning:

    - Kontroller at du oppga riktig mappe
    - Skulle det være ønskelig å ikke ha med en fil, lag en tom en med samme navn

??? failure "`GRANT`-setningen feiler i Databricks med `principal does not exist`"
Sannsynlig årsak: Gruppen eller brukeren som hadde tilgang er slettet eller endret siden backupen ble tatt.

    Løsning:

    - Verifiser principalen under innstillinger og tilpass SQL-en før du kjører den.

## Rydd opp

Fjern eventuelle midlertidige ressurser, slik som S3-bøtter for mellomlagring.

## Relatert innhold

- [Backup](../../om-plattformen/konsepter/backup.md) — hvorfor backup er satt opp slik den er
- [Gjenopprette etter feil i pipelines](gjenopprette-etter-feil.md)
- [`scripts/restore/generate_privilege_sql.py`](../../../scripts/restore/generate_privilege_sql.py) (scriptet er ikke tilgjengelig gjennom dokumentasjonssiden)
