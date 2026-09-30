---
title: Koble VS Code til Databricks
description: Kjør kode på Databricks direkte fra VS Code med den offisielle utvidelsen.
diataxis: how-to
---

# Koble VS Code til Databricks

Du kan bruke en hvilken som helst teksteditor mot plattformen. Men bruker du VS Code,
lar den offisielle Databricks-utvidelsen deg kjøre fila du redigerer direkte på
workspacet, uten å pakke eller deploye noe først. Denne guiden viser hvordan du kobler
utvidelsen til workspacet ditt og kjører en fil på serverless compute.

Slik henger delene sammen:

```mermaid
flowchart LR
    A[VS Code<br/>med Databricks-utvidelsen] -->|laster opp og kjører| B[Databricks-workspace]
    B --> C[Compute]
```

## Før du begynner

Sørg for at du har:

- Gjennomført [Sett opp utviklingsmiljøet](../../kom-i-gang/dev-setup.md), spesielt
  innloggingen med `databricks auth login`, siden utvidelsen gjenbruker profilene i
  `~/.databrickscfg`.
- [VS Code](https://code.visualstudio.com/) installert.

## Trinn 1: Installer anbefalte utvidelser

Vi har laget en [`extensions.json`](https://github.com/oslokommune/padda-golden-path/blob/main/.vscode/extensions.json)
som lister utvidelsene vi anbefaler: den offisielle Databricks-utvidelsen, Ruff for
formatering og linting av Python, og YAML-støtte for bundle-konfigurasjon. Legger du fila
i prosjektet ditt, foreslår VS Code å installere utvidelsene når du åpner mappa.

1. Opprett en tom mappe `databricks-demo` og åpne den i VS Code (**File → Open Folder**).
2. Lag mappa `.vscode` og lagre en kopi av `extensions.json` der.
3. Klikk **Install** i varselet fra VS Code om anbefalte utvidelser. Får du ikke noe
   varsel, åpner du **Extensions**-panelet, skriver `@recommended` i søkefeltet og
   installerer utvidelsene under **Workspace Recommendations**.

## Trinn 2: Koble til workspacet

1. Klikk på Databricks-ikonet i sidepanelet.
2. Klikk **Create configuration**.
3. Oppgi workspace-URL-en din, og velg autentiseringsprofilen du opprettet i [Sett opp
   utviklingsmiljøet](../../kom-i-gang/dev-setup.md#logg-inn-i-databricks).
4. Klikk **Select a cluster** og velg **Serverless**.

## Trinn 3: Kjør kode på Databricks

Lag en fil `demo.py` i mappa du åpnet, med dette innholdet:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

df = spark.range(0, 5)
df.show()
```

Høyreklikk på fila og velg **Run on Databricks** → **Run File as Workflow**. Utvidelsen
laster opp fila til workspacet og kjører den som en jobb på serverless compute.

## Bekreft resultatet

I fanen som åpnes skal du se en tabell med fem rader. Da går koden din fra editoren, via
workspacet, til kjøring på Databricks-compute.

## Relatert innhold

**Guider:**

- [Ta i bruk bundles](ta-i-bruk-bundles.md), for når koden skal pakkes og deployes til
  Databricks
- [`bundles/vscode_demo`](https://github.com/oslokommune/padda-databrikker/tree/main/bundles/vscode_demo)
  i `padda-databrikker` viser et komplett prosjekt med notebook, wheel-bygging og
  bundle-konfigurasjon

**Kom i gang:**

- [Sett opp utviklingsmiljøet](../../kom-i-gang/dev-setup.md)
