---
title: Håndtere secrets
description: Hvordan opprette og bruke Databricks secrets for hemmeligheter som API-nøkler og passord.
diataxis: how-to
icon: lucide/construction
---

# Håndtere secrets

!!! info "Opprinnelse"
    Denne siden er omskrevet fra `docs/guides/developer/secrets.md`.

Denne guiden er ikke ferdig skrevet ennå.

Bør dekke:

- Opprette et secret scope og lagre en hemmelighet
- Lese en secret i en notebook
- Konfigurere tilgang til secret scopes
- Verifisere at secreten er tilgjengelig

## Viktig om tilgang

!!! warning "Secrets er ikke fullstendig skjult"
    Det er ikke en garanti fra Databricks på at secrets ikke blir tilgjengelig for admins:

    > Workspace admins, secret creators, and users who have been granted permission can access and read Databricks secrets. Although Databricks attempts to redact secret values in notebook outputs, it is not possible to fully prevent these users from viewing secret contents. Always assign secret access permissions carefully to protect sensitive information.

## Opprette en secret scope

```bash
databricks secrets create-scope eksempel-scope
```

## Lagre en secret

```bash
databricks secrets put-secret --json '{
  "scope": "eksempel-scope",
  "key": "eksempel",
  "string_value": "eksempel-verdi"
}'
```
