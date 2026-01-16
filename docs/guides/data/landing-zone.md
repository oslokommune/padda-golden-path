# Landing zone

Landing zone er koblet til hvert workspace en S3-bucket opprettes for innkommende data. Hver landing zone har en liste med "sendere" som skal laste opp data til bucketen. For hver sender blir det opprettet tre prefikser (green, yellow, red) med tilhorende brukere som kan laste opp til disse, etter skjemaet:

`s3://bucket_name/sender_name/confidentiality_color/`

## Struktur og tilgang

- 1:1, Ett workspace har en landing zone-bucket
- Hver sender representerer en ekstern aktør som skal kunne laste opp filer.
- For hver sender opprettes tre sub-prefikser (green/yellow/red).
- For hvert prefix lages en IAM-bruker slik at en bruker kun kan laste opp til sitt eget område.

## Tilgang til IAM-brukere

For hver bruker kan det utstedes sikkerhetsnøkler for å gi tilgang til brukeren. Disse må formiddles til den tjenesten eller mennesket som skal bruke de over sikker kanal.

## Bruk av sikkerhetsnøkler

### Testing

En enkel måte å teste nøklene på er ved å bruke AWS CLI. Her overføres en fil fra lokal maskin til landing zone:

```bash
AWS_PROFILE="key-test" aws s3 cp test.txt s3://69d82-padda-landing-zone/testing_bucket/green/test.txt
```

Konfigurasjonsfilen `~/.aws/config` ser da slik ut:

```ini
[profile key-test]
region = eu-west-1
aws_access_key_id = OPELCORSAFOREVER
aws_secret_access_key = LEATHERSEATSTASTEBETTERTHANCHOCOLATE
```
