---
title: Laste opp filer til landing zone
description: Hvordan be om en landing zone-sender og laste opp filer via S3.
diataxis: how-to
icon: lucide/split
---

# Laste opp filer til landing zone

Landing zone er en S3-bucket som opprettes for hvert Databricks-workspace for innkommende data. Hver landing zone har en liste med "sendere" som skal laste opp data til bucketen. For hver sender blir det opprettet tre prefikser (green, yellow, red) med tilhørende brukere som kan laste opp til disse, etter skjemaet:

`s3://bucket_name/sender_name/confidentiality_color/`

## Hvordan får jeg en landing zone-sender?

Landing zone-bucketen administreres av plattformteamet via Terraform. Du oppretter **ikke** bucketen selv.

**Slik ber du om en sender:**

1. Kontakt plattformteamet via [#dig-dataspeilet](https://oslokommune.slack.com/archives/C01SFNFEXK7)
2. Oppgi:
    - Hvilket workspace du tilhører
    - Ønsket sendernavn (f.eks. `min-app`)
    - Eventuell IP-begrensning for opplasting
3. Plattformteamet oppretter senderen og du mottar IAM-nøkler over sikker kanal

## Kobling til Databricks

Landing zone er automatisk tilgjengelig i Databricks via en **External Location** som plattformteamet setter opp. Du trenger ikke gjøre noe ekstra for å koble S3 til Databricks — det er allerede på plass.

For å lese data fra landing zone i en notebook:

```python
# Med Auto Loader (anbefalt for inkrementell innlasting)
df = (
    spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "parquet")
    .option("cloudFiles.schemaLocation", "/tmp/schema/min-app")
    .load("s3://69d82-workspace-landing-zone/min-app/green/")
)

# Eller med enkel batch-lesning
df = spark.read.format("parquet").load(
    "s3://69d82-workspace-landing-zone/min-app/green/2026/02/17/"
)
```

Se [Din første datapipeline](../../kom-i-gang/din-forste-datapipeline.md) for en komplett oversikt over hele dataflyten.

## Bruk av sikkerhetsnøkler

### Testing

En enkel måte å teste nøklene på er ved å bruke AWS CLI. Her overføres en fil fra lokal maskin til landing zone:

```bash
AWS_PROFILE="key-test" aws s3 cp test.txt s3://69d82-padda-landing-zone/test_sender/green/test.txt
```

Konfigurasjonsfilen `~/.aws/config` ser da slik ut:

```ini
[profile key-test]
region = eu-west-1
aws_access_key_id = DIN_ACCESS_KEY
aws_secret_access_key = DIN_SECRET_KEY
```

### Produksjon

I produksjon bruker du AWS SDK for ditt språk. SDK-et finner nøklene automatisk via en prioritert credential chain (environment variables, `~/.aws/config`, `~/.aws/credentials`, m.m.).

**Python (boto3):**
```python
import boto3

s3 = boto3.client("s3", region_name="eu-west-1")
s3.upload_file(
    "data.parquet",
    "69d82-workspace-landing-zone",
    "min-app/green/2026/02/17/data.parquet",
)
```

Se credential-dokumentasjon for ditt språk:

- [Python (boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)
- [Java (DefaultCredentialsProvider)](https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/auth/credentials/DefaultCredentialsProvider.html)
- [Rust (DefaultCredentialsChain)](https://docs.rs/aws-config/latest/aws_config/default_provider/credentials/struct.DefaultCredentialsChain.html)
- [.NET (FallbackCredentialsFactory)](https://docs.aws.amazon.com/sdk-for-net/v3/developer-guide/creds-assign.html)

Felles for alle er at det er en prioritert rekkefølge av steder SDK-et ser etter credentials. I produksjon anbefaler vi Secrets Manager eller Parameter Store fremfor å lagre nøkler i miljøvariabler eller filer.
