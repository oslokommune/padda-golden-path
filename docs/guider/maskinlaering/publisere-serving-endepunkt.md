---
title: Publisere en modell som serving-endepunkt
description: Hvordan slå på serving-endepunktet i ML-eksempelet, velge modellversjon, kalle endepunktet fra Python og fra en Lambda, og hva det koster.
diataxis: how-to
---

# Publisere en modell som serving-endepunkt

Denne guiden viser hvordan du publiserer en registrert modell som et
HTTP-endepunkt med Databricks Model Serving. ML-eksempelet i malen har
endepunktet ferdig definert, men slått av. Du slår det på når noen faktisk
trenger prediksjoner på forespørsel.

!!! info "Sett opp ved behov"
    Batch-inferens er standardvalget på plattformen. Les [Batch eller
    endepunkt?](../../om-plattformen/konsepter/maskinlaering.md#batch-eller-endepunkt)
    før du går videre. Et endepunkt koster mens det er aktivt og gir et ekstra
    rettighetslag å forvalte.

## Før du begynner

Sørg for at du har:

- En registrert modell med minst én versjon, for eksempel etter [Trene og
  registrere en modell](trene-og-registrere-modell.md)
- `EXECUTE` på modellen (du blir eier av endepunktet)
- Avklart hvem som skal kalle endepunktet, og fra hvor

## Trinn 1: Ta endepunktet inn i bundlen

Endepunktet ligger i `resources/optional/example_ml.serving.yml`, utenfor
`include`-mønsteret. Legg mappen til i `databricks.yml`:

```yaml
include:
  - "resources/*.yml"
  - "resources/optional/*.yml"
```

Ressursen ser slik ut:

```yaml
resources:
  model_serving_endpoints:
    example_ml_endpoint:
      name: romledighet
      config:
        served_entities:
          - entity_name: ${var.catalog}.${resources.schemas.example_ml_schema.name}.${resources.registered_models.example_ml_model.name}
            entity_version: ${var.ml_model_version}
            workload_size: Small
            scale_to_zero_enabled: true
      tags:
        - key: CostTeam
          value: padda
        - key: CostProcess
          value: Serve
```

Bytt `CostTeam` til teamet ditt.

## Trinn 2: Velg modellversjon

Et endepunkt serverer et versjonsnummer, ikke et alias. Finn versjonen
`padda` peker på:

```bash
databricks model-versions get-by-alias <katalog>.<skjema>.romledighet padda -p <profil>
```

Sett den som `ml_model_version` når du deployer. Vil du ha verdien fast, sett
den under `variables` i targetet i stedet.

## Trinn 3: Deploy

```bash
databricks bundle validate -t stage -p <profil> --var ml_model_version=1
databricks bundle deploy -t stage -p <profil> --var ml_model_version=1
```

Endepunktet bygger et eget miljø fra kravene modellen ble logget med, og
starter. Første gang tar det typisk 10 til 20 minutter. Følg med:

```bash
databricks serving-endpoints get romledighet -p <profil>
```

Vent til `state.ready` er `READY`.

!!! note "Navn i development-modus"
    Endepunktet får ikke `dev_`-prefiks, men modellen det peker på har det.
    Bundlen setter riktig modellnavn selv via ressursreferansen.

## Trinn 4: Kall endepunktet

Endepunktet tar rader med nøyaktig kolonnene i `FEATURE_COLUMNS` og svarer
med sannsynligheten for at rommet er booket. Adressen er
`https://<workspace-host>/serving-endpoints/romledighet/invocations`.

=== "Python"

    ```python
    import requests

    host = "https://<workspace-host>"
    token = "<personlig token eller service principal-token>"

    rows = [
        {
            "ukedag": 2.0, "time_num": 10.0, "etasje": 3.0, "kapasitet": 6.0,
            "har_video": 1.0, "booket_forrige_uke": 1.0,
            "andel_booket_siste_4_uker": 0.75,
            "bygg_radhuset": 1.0, "bygg_grensen": 0.0, "bygg_storgata": 0.0,
        }
    ]
    response = requests.post(
        f"{host}/serving-endpoints/romledighet/invocations",
        headers={"Authorization": f"Bearer {token}"},
        json={"dataframe_records": rows},
        timeout=60,
    )
    response.raise_for_status()
    print(response.json())
    ```

=== "Lambda i padda-databrikker"

    Hent tokenet fra SSM Parameter Store slik [Håndtere
    secrets](../hente-inn-data/haandtere-secrets.md#ssm-parameter-store-lambda-fargate)
    beskriver, og kall endepunktet med `urllib` for å slippe ekstra
    avhengigheter:

    ```python
    import json
    import os
    import urllib.request

    import boto3

    ssm = boto3.client("ssm")
    token = ssm.get_parameter(Name=os.environ["TOKEN_PARAMETER"], WithDecryption=True)["Parameter"]["Value"]
    host = os.environ["DATABRICKS_HOST"]

    def handler(event, context):
        body = json.dumps({"dataframe_records": event["rows"]}).encode()
        request = urllib.request.Request(
            f"{host}/serving-endpoints/romledighet/invocations",
            data=body,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    ```

    Bruk en service principal med `CAN_QUERY` på endepunktet, ikke en
    personlig bruker.

Svaret er en liste med én sannsynlighet per rad:

```json
{"predictions": [[0.83]]}
```

Gi andre tilgang til å kalle endepunktet med `permissions` på ressursen:

```yaml
      permissions:
        - group_name: <teamets gruppe>
          level: CAN_QUERY
```

## Trinn 5: Bytt versjon, og forstå kostnaden

Når treningsjobben har laget en ny "padda", deployer du endepunktet på nytt
med det nye versjonsnummeret. Databricks bytter versjon uten nedetid.

Endepunktet faktureres per tid det er oppe. Med `scale_to_zero_enabled` skrur
det seg av etter en periode uten trafikk, og det første kallet etterpå venter
på oppstart, typisk noen minutter. Er det uakseptabelt for konsumenten, må du
skru av scale-to-zero og betale for et endepunkt som alltid er oppe.
Kostnaden vises under `CostProcess: Serve` i kostnadsrapportene, se [Tagging
av kostnader](../overvaake-og-drifte/kostnadstagging.md).

## Bekreft resultatet

```bash
databricks serving-endpoints get romledighet -p <profil> -o json | jq '{ready: .state.ready, version: .config.served_entities[0].entity_version}'
```

Forventet utdata:

```json
{
  "ready": "READY",
  "version": "1"
}
```

Et testkall som i trinn 4 skal gi et tall mellom 0 og 1.

## Rydd opp

Fjern `resources/optional/*.yml` fra `include` og deploy på nytt. Bundlen
sletter endepunktet; modellen og tabellene beholdes.

## Feilsøking

??? failure "Endepunktet står lenge i `NOT_READY` eller feiler ved oppstart"
    Endepunktet bygger et miljø fra modellens `requirements.txt`. Feiler
    byggingen, vises loggen under **Serving** i workspacet.

    Løsning:

    - Sjekk at modellen ble logget med `torch` i kravene (eksempelet gjør det).
    - Sjekk at versjonen finnes: `databricks model-versions list <modell>`.

??? failure "`403` ved kall"
    Kalleren mangler `CAN_QUERY` på endepunktet, eller tokenet tilhører feil
    workspace.

    Løsning:

    - Legg kalleren til under `permissions` på ressursen, og bruk et token fra
      samme workspace som endepunktet.

??? failure "`400` med melding om input-skjema"
    Radene mangler kolonner eller har feil type i forhold til signaturen.

    Løsning:

    - Send nøyaktig `FEATURE_COLUMNS` som tall. Kolonnenavn og rekkefølge står i
      [MLflow og modellregister](../../referanse/mlflow-og-modellregister.md#tabeller).

## Relatert innhold

- [Trene og registrere en modell](trene-og-registrere-modell.md)
- [Kjøre batch-inferens med en registrert modell](batch-inferens.md)
- [MLflow og modellregister (referanse)](../../referanse/mlflow-og-modellregister.md)
- [Maskinlæring på plattformen](../../om-plattformen/konsepter/maskinlaering.md)
- [Håndtere secrets](../hente-inn-data/haandtere-secrets.md)
