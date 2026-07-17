---
title: Sett opp utviklingsmiljøet
description: Installer verktøyene du trenger og logg inn i Databricks fra kommandolinja.
diataxis: tutorial
---

# Sett opp utviklingsmiljøet

I dette steget installerer du verktøyene du trenger for å utvikle mot dataplattformen. Når
du er ferdig, har du:

- [uv](https://docs.astral.sh/uv/) for å håndtere Python-versjoner og avhengigheter
- [Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/) installert og
  innlogget i workspacet ditt
- En lokal klone av
  [`padda-golden-path`](https://github.com/oslokommune/padda-golden-path)

## Før du starter

- Du har [fått tilgang til plattformen](slik-faar-du-tilgang.md).
- Du er på macOS eller Linux. Er du på Windows, er
  [WSL](https://learn.microsoft.com/en-us/windows/wsl/) en mulighet.

## Installer uv

Vi bruker uv som pakke- og prosjektverktøy for Python. Installer det med:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Sjekk at installasjonen fungerer:

```bash
uv --version
```

![Terminalutskrift fra uv --version](uv-version.png)

## Installer Databricks CLI

Databricks CLI bruker du til å logge inn, kjøre kommandoer mot workspacet og deploye
bundles. Velg installasjonsmetode:

=== "Homebrew"

    Har du Homebrew, installerer du CLI-en slik:

    ```bash
    brew tap databricks/tap
    brew trust databricks/tap
    brew install databricks
    ```

    !!! note "Feiler `brew trust`?"
        Fra Homebrew 6.0.0 må du eksplisitt stole på taps fra tredjepart. Får
        du «Unknown command» på `brew trust`, har du en eldre Homebrew-versjon
        og kan hoppe over det steget.

=== "curl"

    Har du ikke Homebrew (for eksempel på Linux), kan du bruke
    installasjonsskriptet:

    ```bash
    curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
    ```

Sjekk at installasjonen fungerer:

```bash
databricks -v
```

![Terminalutskrift fra databricks -v](databricks-version.png)

### Autofullføring

CLI-en kan generere autofullføring for skallet ditt, uavhengig av installasjonsmetode:

=== "zsh"

    ```bash
    echo 'autoload -U compinit; compinit' >> ~/.zshrc
    echo 'source <(databricks completion zsh)' >> ~/.zshrc
    ```

=== "bash"

    ```bash
    echo 'source <(databricks completion bash)' >> ~/.bashrc
    ```

Se `databricks completion --help` for flere skall.

## Logg inn i Databricks

Plattformen bruker single sign-on via Entra ID (se [Slik får du
tilgang](slik-faar-du-tilgang.md#logg-inn)), så du trenger ingen egne Databricks-passord
eller tokens. Logg inn med:

```bash
databricks auth login --host <workspace-url> --profile <profilnavn>
```

Bruk workspace-URL-en til teamet ditt, og velg et profilnavn som gjør det lett å kjenne
igjen workspacet. Er du usikker på hvilken workspace-URL du skal bruke, [ta kontakt med
Dataspeilet](../hjelp/index.md#kontakt-plattformteamet). Innloggingssiden åpnes i
nettleseren, og når du er innlogget lagres profilen i `~/.databrickscfg`.

!!! note "Flere workspaces?"

    Har du tilgang til flere workspaces (for eksempel stage og prod), logger du inn én
    gang per workspace, med en egen profil for hvert av dem — se [Velge
    CLI-profil](../guider/bearbeide-data/ta-i-bruk-bundles.md#velge-cli-profil).

Sjekk at innloggingen er gyldig:

```bash
databricks auth profiles
```

## Klon `padda-golden-path`

Flere av guidene bruker malene og eksemplene i
[`padda-golden-path`](https://github.com/oslokommune/padda-golden-path) — blant annet
bundle-malene i `bundle-templates/` og eksempelprosjektene i `examples/`. Klon repoet:

```bash
git clone git@github.com:oslokommune/padda-golden-path.git
```

## Velg teksteditor

Du kan bruke den teksteditoren du foretrekker. Bruker du VS Code, følger det med anbefalte
utvidelser og innstillinger i `.vscode/`-mappa i repoet, og du kan [koble VS Code direkte
til Databricks](koble-vscode-til-databricks.md).

## Neste steg

Utviklingsmiljøet er klart. Gå videre til [Bygg din første
datapipeline](din-forste-datapipeline.md).
