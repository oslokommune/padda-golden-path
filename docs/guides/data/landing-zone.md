# Landing zone

Landing zone er koblet til hvert workspace en S3-bucket opprettes for innkommende data. Hver landing zone har en liste med "sendere" som skal laste opp data til bucketen. For hver sender blir det opprettet tre prefikser (green, yellow, red) med tilhorende brukere som kan laste opp til disse, etter skjemaet:

`s3://bucket_name/sender_name/confidentiality_color/`

## Struktur og tilgang

- 1:1 - Et workspace har en og bare en landing zone-bucket
- Hver sender representerer en ekstern aktør som skal kunne laste opp filer.
- For hver sender opprettes tre sub-prefikser (green/yellow/red).
- For hvert prefix lages en IAM-bruker slik at en bruker kun kan laste opp til sitt eget område.

## Tilgang til IAM-brukere

For hver bruker kan det utstedes sikkerhetsnøkler for å gi tilgang til brukeren. Disse må formiddles til den tjenesten eller mennesket som skal bruke de over sikker kanal.

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
aws_access_key_id = OPELCORSAFOREVER
aws_secret_access_key = LEATHERSEATSTASTEBETTERTHANCHOCOLATE
```

### Produksjon

Nøyaktig hvilken mekanisme man bruker i prod kommer litt an på, men la oss si at du bygger et program i Rust med AWS SDK. SDKet vil da finne nøklene via noe a la [`DefaultCredentialsChain`](https://docs.rs/aws-config/latest/aws_config/default_provider/credentials/struct.DefaultCredentialsChain.html). Her er et [eksempel på hvordan filkopiering kan gjøres](https://github.com/awsdocs/aws-doc-sdk-examples/blob/main/rustv1/examples/s3/src/bin/copy-object.rs). Eksempelet bruker [`RegionProviderChain`](https://docs.rs/aws-config/latest/aws_config/meta/region/struct.RegionProviderChain.html), men det er bare en wrapper rundt `DefaultCredentialsChain`. Det er mange måter å gi nøklene til `DefaultCredentialsChain` på, men det går helt greit å legge de i `~/.aws/config`, akkurat som i avsnittet om testing. Andre språk kan være litt mer implisitte rundt det hele, men fungerer på samme måte. Her er dokumentasjonen for [Javas DefaultCredentialsProvider](https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/auth/credentials/DefaultCredentialsProvider.html) og [tilsvarende i Python](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html).
