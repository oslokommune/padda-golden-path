Løsningsforslag

1) padda-iac

inneholder: Landing zone S3 buckets, KMS nøkler

opprette standard module for ingestion Lambdas

IAM definerer:
Lambda execution rolle: kun skrive til s3://landing-zone/...

GitHub deploy rolle: kun oppdatere lambda kode.

2) padda-golden-path

Skal inneholde

en template for “API Ingestion Lambda”

i delt bibliotek (logging, standardisert output (delta table))

En gjenbrukbar GitHub Action (slik at dataproduktteam kan kopiere)

3) sye og andre dataproduktteam sine repoer

inneholder

Lambda kode + tester

GitHub Action gjenbrukt fra padda-golden-path