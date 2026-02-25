# Secrets

TODO:
1password bruk og databricks secrets beskrevet bedre.

Det er ikke en garanti fra Databricks på at secrets ikke blir tilgjengelig for admins etc:

> Workspace admins, secret creators, and users who have been granted permission can access and read Databricks secrets. Although Databricks attempts to redact secret values in notebook outputs, it is not possible to fully prevent these users from viewing secret contents. Always assign secret access permissions carefully to protect sensitive information.

Men for å lage:
```bash
databricks secrets create-scope eksempel-scope
```

```bash
databricks secrets put-secret --json '{
  "scope": "eksempel-scope",
  "key": "eksempel",
  "string_value": "eksempel-verdi"
}'
```
