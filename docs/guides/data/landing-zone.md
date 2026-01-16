# Landing zone

Landing zone er koblet til hvert workspace en S3-bucket opprettes for innkommende data. Hver landing zone har en liste med "sendere" som skal laste opp data til bucketen. For hver sender blir det opprettet tre prefikser (green, yellow, red) med tilhorende brukere som kan laste opp til disse, etter skjemaet:

`s3://bucket_name/sender_name/confidentiality-color/`

## Struktur og tilgang

- 1:1, Ett workspace har en landing zone-bucket
- Hver sender representerer en ekstern aktør som skal kunne laste opp filer.
- For hver sender opprettes tre prefikser (green/yellow/red). IAM-brukere kobles til prefiksene slik at de kun kan laste opp til sitt eget område.


## tilgang til IAM-brukere
