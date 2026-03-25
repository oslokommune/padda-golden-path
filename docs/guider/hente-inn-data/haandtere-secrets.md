---
title: Håndtere secrets
description: Hvordan håndtere hemmeligheter for Databricks-notebooks og Lambda-funksjoner.
diataxis: how-to
---

# Håndtere secrets

Denne guiden dekker to separate system for hemmeligheter på plattformen:

- **Databricks secrets** — for notebooks og jobber som kjører i Databricks
- **SSM Parameter Store** — for Lambda-funksjoner og Fargate-tasks som kjører i AWS

## Databricks secrets

Bruk Databricks secret scopes til å lagre API-nøkler, passord og tokens som notebooks og jobber trenger.

### Steg 1 — Opprett en secret scope

```bash
databricks secrets create-scope my-scope
```

### Steg 2 — Lagre en secret

```bash
databricks secrets put-secret --json '{
  "scope": "my-scope",
  "key": "api-key",
  "string_value": "din-verdi"
}'
```

### Steg 3 — Les secreten i en notebook

```python
api_key = dbutils.secrets.get(scope="my-scope", key="api-key")
```

Verdien redigeres bort i notebook-output, men se advarselen under.

### Steg 4 — Sjekk tilgang

Liste secrets i et scope:

```bash
databricks secrets list-secrets my-scope
```

Liste hvem som har tilgang:

```bash
databricks secrets list-acls my-scope
```

Gi tilgang til en gruppe:

```bash
databricks secrets put-acl my-scope "data-engineers" READ
```

!!! warning "Secrets er ikke fullstendig skjult"
    Workspace-administratorer, de som opprettet secreten, og brukere med tildelt tilgang kan lese Databricks-secrets. Selv om Databricks redigerer bort secret-verdier i notebook-output, er det ikke mulig å fullstendig hindre disse brukerne fra å se innholdet.

---

## SSM Parameter Store (Lambda / Fargate)

Lambda-funksjoner og Fargate-tasks bruker AWS Systems Manager (SSM) Parameter Store for hemmeligheter. Deploy-workflowen synkroniserer automatisk secrets fra GitHub til SSM.

### Steg 1 — Legg til en GitHub Environment secret

1. Gå til repoets **Settings** → **Environments** → **stage**
2. Klikk **Add secret**
3. Gi secreten et navn med prefikset `SSM_`, for eksempel: `SSM_MY_API_KEY`
4. Skriv inn verdien

### Steg 2 — Deploy

Push eller trigger en deploy. Workflowen synkroniserer alle `SSM_`-prefiksede secrets til SSM Parameter Store automatisk:

| GitHub secret | SSM-parameterbane |
|---|---|
| `SSM_MY_API_KEY` | `/<workspace-name>/my-api-key` |
| `SSM_DATABASE_URL` | `/<workspace-name>/database-url` |

Navnekonvensjonen: fjern `SSM_`, gjør om til små bokstaver, erstatt understrek med bindestrek.

### Steg 3 — Referer til SSM-parameteren i template.yaml

Send parameterbanen som en miljøvariabel slik at funksjonen vet hvor den skal lete:

```yaml
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      # ...
      Environment:
        Variables:
          API_KEY_PARAM: /<workspace-name>/my-api-key
```

!!! warning "Send parameterstien, ikke verdien"
    Miljøvariabelen inneholder *banen* til secreten i SSM, ikke selve secreten. Funksjonen henter den faktiske verdien ved kjøretid. Dette unngår å eksponere hemmeligheter i CloudFormation-templater eller miljøvariabel-listinger.

### Steg 4 — Les verdien ved kjøretid

```python
import os
import boto3


def get_secret(param_name: str) -> str:
    """Fetch a SecureString from SSM Parameter Store."""
    ssm = boto3.client("ssm")
    response = ssm.get_parameter(Name=param_name, WithDecryption=True)
    return response["Parameter"]["Value"]


# I handleren eller hovedfunksjonen din:
api_key = get_secret(os.environ["API_KEY_PARAM"])
```

!!! warning "Aldri logg secret-verdien"
    Logg parameternavnet og lengden for å verifisere at den ble lest riktig, men aldri den faktiske verdien:

    ```python
    print(f"Read secret from {param_name} (length={len(secret_value)})")
    ```

### Steg 5 — Gi Lambda tilgang til SSM (hvis nødvendig)

`AWSLambdaBasicExecutionRole` managed policy inkluderer **ikke** SSM-tilgang. Hvis funksjonen din leser fra SSM, tillater deploy-pipelinens permission boundary det allerede. Men hvis du trenger å begrense tilgangen til spesifikke parametere, legg til en inline policy:

```yaml
Policies:
  - PolicyName: SsmReadAccess
    PolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Action:
            - ssm:GetParameter
          Resource:
            - !Sub "arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/<workspace-name>/*"
```

## Hvilket system skal du bruke?

| Kontekst | Secret-system | Hvorfor |
|----------|--------------|---------|
| Databricks notebook eller jobb | **Databricks secrets** | Integrert med `dbutils`, redigert bort i output |
| Lambda-funksjon | **SSM Parameter Store** | Synkronisert via CI/CD, hentet ved kjøretid med boto3 |
| Fargate-task | **SSM Parameter Store** | Samme mønster som Lambda |
