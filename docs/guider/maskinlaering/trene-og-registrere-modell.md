---
title: Trene og registrere en modell
description: Hvordan generere ML-eksempelet fra bundle-malen, deploye det, laste opp PyTorch til volumet og kjøre treningsjobben som registrerer modellen i Unity Catalog.
diataxis: how-to
---

# Trene og registrere en modell

Denne guiden tar deg fra en ny bundle til en registrert modell i Unity Catalog
med aliaset `padda`. Du bruker ML-eksempelet i bundle-malen, som trener en
PyTorch-modell på syntetiske møteromsbookinger. Til slutt bytter du ut
eksempeldataene med dine egne.

## Før du begynner

Sørg for at du har:

- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install.html)
  installert og en profil mot workspacet ditt
- [uv](https://docs.astral.sh/uv/) installert
- `USE_CATALOG` og `CREATE_SCHEMA` på katalogen du skal bruke. Bundlen
  oppretter sitt eget skjema.
- Lest [Maskinlæring på
  plattformen](../../om-plattformen/konsepter/maskinlaering.md), slik at du
  vet hva som havner hvor

Guiden forutsetter at du kjenner [Ta i bruk bundles](../utvikle-og-deploye/ta-i-bruk-bundles.md).

## Trinn 1: Generer bundlen med ML-eksempelet

Kjør `bundle init` mot malen og svar `yes` på `include_ml_workflow`:

```bash
databricks bundle init /sti/til/padda-golden-path/bundle-templates -p <profil>
```

Spørsmålet stilles når `setup_type` er `default` eller `tailored`. Vil du
bare ha ML-delen, velg `tailored`, svar `no` på eksempeljobbene og `yes` på
ML. Du kan også svare i en fil:

```json title="svar.json"
{
  "catalog_name": "<din_katalog>",
  "stage_workspace_host": "https://<stage-workspace>.cloud.databricks.com",
  "prod_workspace_host": "https://<prod-workspace>.cloud.databricks.com",
  "domain_name": "moteromsbooking",
  "domain_description": "Ledighet for møterom",
  "setup_type": "tailored",
  "include_example_jobs": "no",
  "empower_vscode": "no",
  "include_ml_workflow": "yes"
}
```

```bash
databricks bundle init /sti/til/padda-golden-path/bundle-templates --config-file svar.json -p <profil>
```

Du får denne strukturen i tillegg til det vanlige prosjektet:

```
moteromsbooking/
  resources/
    example_ml.schema.yml            # skjemaet bundlen eier
    example_ml.volume.yml            # volumet wheels
    example_ml.experiment.yml        # MLflow-eksperiment
    example_ml.registered_model.yml  # den registrerte modellen
    example_ml.job.yml               # jobben: generate_data -> build_features -> train -> predict
    optional/
      example_ml.serving.yml         # endepunkt, ikke inkludert
  scripts/
    upload_ml_wheels.sh              # laster PyTorch opp til volumet
  src/moteromsbooking/ml/            # data, features, model, registry, train, predict, tasks
  tests/test_ml_*.py                 # enhetstester uten Spark
```

## Trinn 2: Sett variablene per target

Åpne `databricks.yml` og sett `catalog` og `ml_schema` for hvert target.
`ml_schema` er skjemaet bundlen oppretter; bruk navnet på bruksområdet:

```yaml
targets:
  stage:
    mode: development
    default: true
    workspace:
      host: https://<stage-workspace>.cloud.databricks.com
    variables:
      catalog: <din_katalog>
      schema: bronze_default
      ml_schema: moteromsbooking
```

`ml_consumer_group` styrer hvem som får lese prediksjonene og kjøre modellen.
Standardverdien `account users` passer i et utviklingsworkspace; i prod setter
du teamets gruppe.

## Trinn 3: Valider og deploy

```bash
uv sync
uv run pytest
databricks bundle validate -t stage -p <profil>
databricks bundle deploy -t stage -p <profil>
```

Deployen oppretter skjemaet, volumet, eksperimentet, den registrerte modellen
(uten versjoner ennå) og jobben. I development-modus får skjemaet og modellen
prefikset `dev_<brukernavn>_`; jobben får de faktiske navnene fra bundlen, så
du trenger ikke endre noe. Se navnene med:

```bash
databricks bundle summary -t stage -p <profil>
```

## Trinn 4: Last opp PyTorch til volumet

Compute på plattformen har ikke internett, og PyTorch er ikke en del av
serverless-miljøet. Skriptet laster ned `torch` for Linux x86_64 og Python
3.12 (serverless-miljøets versjon) sammen med avhengighetene som mangler i
miljøet, og laster dem opp til volumet `wheels` i skjemaet bundlen nettopp
opprettet:

```bash
scripts/upload_ml_wheels.sh stage <profil>
```

Dette tar et par minutter første gang (rundt 200 MB). Du gjør det på nytt bare
når du bytter torch-versjon eller miljøversjon.

!!! note "Hvorfor volum og ikke `dist/deps`?"
    [Ta i bruk bundles](../bearbeide-data/ta-i-bruk-bundles.md#tredjepartsbiblioteker)
    anbefaler å pakke små tredjepartsbiblioteker sammen med bundlen. PyTorch
    er for stort til det, så eksempelet bruker et volum som bundlen eier og
    `--no-index --find-links` i jobbmiljøet.

## Trinn 5: Kjør treningsjobben

```bash
databricks bundle run example_ml_job -t stage -p <profil>
```

Jobben har fire tasks. `generate_data` skriver syntetiske rom og bookinger,
`build_features` bygger feature-tabellen, `train` trener og registrerer
modellen, og `predict` skriver prediksjoner for den kommende uken. Første
kjøring tar rundt 15 minutter; det meste er oppstart av miljøet per task.

`train` gjør dette, i rekkefølge:

1. Leser `romledighet_features` og deler etter dato: de siste 14 dagene er
   valideringssett.
2. Åpner en MLflow-kjøring i eksperimentet og logger parametere og
   `train_loss` per epoke.
3. Evaluerer på valideringssettet og logger `val_auc` og `val_accuracy`.
4. Logger modellen med signatur og input-eksempel, og registrerer den som ny
   versjon.
5. Setter aliaset: `padda` hvis `val_auc` er minst like god som dagens
   padda, ellers `utmaner_padda`.

## Trinn 6: Bytt ut eksempeldataene med dine egne

Eksempelet er laget for å byttes ut. Tre steder betyr noe:

- `src/<pakke>/ml/features.py`: `FEATURE_COLUMNS` er kontrakten mellom
  trening og inferens. Endre listen og SQL-en i `feature_sql` til dine
  kolonner, eller erstatt funksjonen med en som leser fra din egen
  feature-tabell. Alle kolonner må være numeriske.
- `src/<pakke>/ml/data.py` og tasken `generate_data`: fjern dem når du har
  ekte data, og la `build_features` lese fra dine tabeller.
- `src/<pakke>/ml/model.py`: `build_model` returnerer et nettverk av
  standardlag. Bytt arkitektur her; behold gjerne prinsippet om bare
  `torch.nn`-lag, så lastes modellen uten at pakken din må være installert.

Enhetstestene i `tests/test_ml_*.py` kjører uten Spark og dekker generatoren,
feature-kontrakten, modellen og alias-regelen. Oppdater dem sammen med koden.

## Bekreft resultatet

Sjekk at aliaset peker på en versjon:

```bash
databricks model-versions get-by-alias <katalog>.<skjema>.romledighet padda -p <profil>
```

Forventet utdata (utdrag):

```json
{
  "version": 1,
  "status": "READY"
}
```

Åpne eksperimentet i workspacet under **Experiments**; kjøringen skal ha
`val_auc` og en modellartefakt. I **Catalog** finner du modellen under skjemaet
med versjon 1 og aliaset `padda`.

## Feilsøking

??? failure "`Library installation failed: ... Unable to find or download the required package`"
    Jobben fant ikke PyTorch. Volumet er tomt, eller `dependencies` i jobbmiljøet
    mangler `--no-index`.

    Løsning:

    - Kjør `scripts/upload_ml_wheels.sh <target> <profil>` og sjekk innholdet med
      `databricks fs ls dbfs:/Volumes/<katalog>/<skjema>/wheels/ -p <profil>`.
    - Feiler bare første forsøk på `generate_data` rett etter en deploy, og
      forsøk to lykkes av seg selv, kan du se bort fra det.

??? failure "`Parent directory does not exist` ved deploy"
    Eksperimentet ligger i en mappe som ikke finnes. MLflow oppretter ikke
    foreldremapper.

    Løsning:

    - Behold eksperimentnavnet rett under brukermappen, slik malen setter det.

??? failure "`PERMISSION_DENIED` på skjema eller modell ved deploy"
    Du mangler `CREATE_SCHEMA` på katalogen, eller skjemaet finnes fra før med
    en annen eier.

    Løsning:

    - Be katalogeier om `USE_CATALOG` og `CREATE_SCHEMA`, eller velg et annet
      `ml_schema`.

??? failure "Finner ikke skjemaet i katalogen"
    I development-modus heter skjemaet `dev_<brukernavn>_<ml_schema>`.

    Løsning:

    - Se de faktiske navnene med `databricks bundle summary -t stage`.

## Rydd opp

`databricks bundle destroy -t stage -p <profil>` fjerner jobben, eksperimentet,
volumet, skjemaet og tabellene. Den registrerte modellen kan bare slettes når
den ikke har versjoner, så slett dem først:

```bash
databricks model-versions list <katalog>.<skjema>.romledighet -p <profil>
databricks model-versions delete <katalog>.<skjema>.romledighet 1 -p <profil>
databricks bundle destroy -t stage -p <profil>
```

Det samme gjelder hvis du endrer ressursnøkkelen eller navnet på modellen:
bundlen må da slette den gamle modellen, og feiler til versjonene er borte.

## Relatert innhold

- [Kjøre batch-inferens med en registrert modell](batch-inferens.md)
- [Publisere en modell som serving-endepunkt](publisere-serving-endepunkt.md)
- [MLflow og modellregister (referanse)](../../referanse/mlflow-og-modellregister.md)
- [Maskinlæring på plattformen](../../om-plattformen/konsepter/maskinlaering.md)
- [Laste opp Python-biblioteker](../bearbeide-data/laste-opp-python-biblioteker.md)
