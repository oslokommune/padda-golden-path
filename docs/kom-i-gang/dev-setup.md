---
title: Sett opp utviklingsmiljøet
description: Hvordan installere verktøy, konfigurere CLI og sette opp IDE for Databricks-utvikling.
diataxis: tutorial
---

# Start her

Denne guiden beskriver hvordan du setter opp utviklingsmiljø og avhengigheter. Per i dag er det Mac og Linux som er støttet, dersom du er på Windows så er WSL en mulighet.

Guiden forutsetter at du har [Homebrew](https://brew.sh/) installert.

## Installere uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Sjekk med:

```bash
uv --version
```
![uv-version](uv-version.png)

## Git config
Det er satt opp en pre-commit-hook i `padda-golden-path/.pre-commit-config.yaml` som kjører ruff.

```bash
uvx pre-commit install
```

## Installere databricks-cli
```bash
brew trust databricks/tap
brew tap databricks/tap
brew install databricks
```

TIP: For tab-completion følg instruksjoner fra Homebrew:

zsh:
```bash
echo fpath+=$(brew --prefix)/share/zsh/site-functions >> ~/.zshrc
echo 'autoload -Uz compinit && compinit' >> ~/.zshrc
zsh
```

Sjekk med:

```bash
databricks -v
```
![databricks version](databricks-version.png)

### Konfigurere databricks-cli

Kjør igjennom guiden for konfigurasjon:
```bash
databricks configure
```
Verdier ligger i 1Password, [ta kontakt med Dataspeilet](../hjelp/index.md#kontakt-plattformteamet) dersom du ikke har tilgang.

## VS Code-spesifikke ting
Det er satt opp en `settings.json` og anbefalte extensions i `.vscode`.
