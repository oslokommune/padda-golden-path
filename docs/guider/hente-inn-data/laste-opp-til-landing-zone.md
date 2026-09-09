---
title: Laste opp filer til landing zone
description: Hvordan be om en landing zone-sender og laste opp filer via S3 med IAM-rolle eller nøkler.
diataxis: how-to
---

# Laste opp filer til landing zone

Denne guiden viser hvordan du får en landing zone-sender og laster opp filer til senderens prefikser (`s3://bucket_name/sender_name/confidentiality_color/`).

Er landing zone nytt for deg? Se [Landing zone-struktur](../../referanse/landing-zone.md) for bøttestruktur, autentiseringsmekanismer og tilgangsmodell.

## Be om en sender

Landing zone-bøtta administreres av plattformteamet via Terraform. Du oppretter **ikke** bøtta selv.

1. Kontakt plattformteamet via [#dig-dataspeilet-support](https://oslokommune.slack.com/archives/C01DE13PLDP)
2. Oppgi:
    - Hvilket workspace du tilhører
    - Ønsket sendernavn (for eksempel `min-app`)
    - AWS-kontonummeret deres, eventuelt ARN-en til en spesifikk rolle i kontoen som skal få lov til å innta ingest-rollen (hvis dere har egen AWS-konto)
    - Eventuell IP-begrensning for opplasting
3. Plattformteamet oppretter senderen:
    - Har dere egen AWS-konto, får dere en **IAM-rolle**: dere mottar rolle-ARN og en **external ID** som må oppgis når rollen inntas
    - Ellers får dere **IAM-nøkler** gjennom 1Password

## Laste opp med IAM-rolle (anbefalt)

Legg inn en profil i `~/.aws/config` som inntar rollen du har fått utlevert:

```ini
[profile landing-zone]
region = eu-west-1
role_arn = DIN_ROLLE_ARN
external_id = DIN_EXTERNAL_ID
source_profile = min-konto
```

`source_profile` peker på profilen med påloggingsinformasjonen for deres egen konto. Kjører applikasjonen på ECS eller EC2 i deres konto, bytt ut `source_profile` med `credential_source = EcsContainer` eller `credential_source = Ec2InstanceMetadata` — da hentes påloggingsinformasjonen automatisk fra kjøremiljøet.

Test tilgangen med AWS CLI:

```bash
aws s3 cp test.txt s3://12345-workspace-landing-zone/min-app/green/test.txt --profile landing-zone
```

I produksjon bruker du AWS SDK for ditt språk. SDK-ene støtter samme profilkonfigurasjon og fornyer den midlertidige rolletilgangen automatisk.

**Python (boto3):**

```python
import boto3

session = boto3.Session(profile_name="landing-zone")
s3 = session.client("s3")
s3.upload_file(
    "data.parquet",
    "12345-workspace-landing-zone",
    "min-app/green/2026/02/17/data.parquet",
)
```

Med dette oppsettet ligger external ID-en i klartekst i `~/.aws/config`. Det er greit på en lokal maskin, men ikke sjekk den inn i versjonskontroll eller bak den inn i et container-image — lagre den i Secrets Manager eller Parameter Store, og sett opp profilen fra den når miljøet bygges.

## Laste opp med IAM-nøkler

Har dere ikke en AWS-konto å innta rollen fra, får dere i stedet IAM-nøkler. Legg dem inn i `~/.aws/config`:

```ini
[profile key-test]
region = eu-west-1
aws_access_key_id = DIN_ACCESS_KEY
aws_secret_access_key = DIN_SECRET_KEY
```

Test nøklene med AWS CLI:

```bash
AWS_PROFILE="key-test" aws s3 cp test.txt s3://12345-workspace-landing-zone/min-app/green/test.txt
```

I produksjon finner AWS SDK-et nøklene automatisk via en prioritert kjede av kilder (miljøvariabler, `~/.aws/config`, `~/.aws/credentials`, med mer). Se SDK-dokumentasjonen for ditt språk:

- [Python (boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)
- [Java (DefaultCredentialsProvider)](https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/auth/credentials/DefaultCredentialsProvider.html)
- [Rust (DefaultCredentialsChain)](https://docs.rs/aws-config/latest/aws_config/default_provider/credentials/struct.DefaultCredentialsChain.html)
- [Go (LoadDefaultConfig)](https://docs.aws.amazon.com/sdk-for-go/v2/developer-guide/configure-gosdk.html)

Lagre nøklene i Secrets Manager eller Parameter Store fremfor miljøvariabler eller filer. Får dere egen AWS-konto senere, kontakt plattformteamet for å bytte til IAM-rolle.

## Se også

- [Landing zone-struktur](../../referanse/landing-zone.md) — bøttestruktur, autentiseringsmekanismer og tilgangsmodell
- [Sette opp Auto Loader](auto-loader.md) — les inn filene fra landing zone til Unity Catalog. Landing zone er allerede koblet til Databricks via en External Location som plattformteamet setter opp
- [Hente data via API](hente-data-via-api.md) — sett opp en serverless-funksjon som henter data fra et eksternt API og skriver til landing zone
- [Bygg din første datapipeline](../../kom-i-gang/din-forste-datapipeline.md) — fra fil i et Volume til bronze- og silver-tabell, steg for steg
