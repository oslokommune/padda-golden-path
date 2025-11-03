# Start her

Denne guiden beskriver hvordan du setter opp devmiljø og avhengigheter. Per idag er det mac og linux som er støttet, dersom du er på windows så er WSL en mulighet.

Guiden forutsetter at du har Homebrew installert, [Homebrew](https://brew.sh/)

# Installere uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
``` 

Sjekk med:

```bash
uv --version
``` 
![uv-version](./images/uv-version.png)

# Installere databricks-cli
```bash
brew tap databricks/tap
brew install databricks
``` 

For tab-completion følg instruksjoner fra Homebrew:

zsh:
```bash
echo fpath+=$(brew --prefix)/share/zsh/site-functions >> ~/.zshrc
echo 'autoload -Uz compinit && compinit' >> ~/.zshrc
zsh
``` 

bash:
```bash
echo fpath+=$(brew --prefix)/share/zsh/site-functions >> ~/.zshrc
echo 'autoload -Uz compinit && compinit' >> ~/.zshrc
bash
```

Sjekk med:

```bash
databricks -v
``` 
![databricks version](./images/databricks-version.png)

## Konfigurere databricks-cli
Det er laget en funksjon 
databricks auth login --host <account-console-url> --account-id <account-id>

# vscode spesifikke ting
Det er satt opp en settings.json og rekommenderte extensions i .vscode

