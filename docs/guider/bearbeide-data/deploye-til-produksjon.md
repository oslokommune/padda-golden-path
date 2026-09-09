---
title: Deploye til produksjon med GitHub Actions
description: Hvordan deploye bundlen til produksjonsworkspacet fra GitHub Actions med OIDC og service principal.
diataxis: how-to
icon: lucide/construction
---

# Deploye til produksjon med GitHub Actions

Denne guiden er ikke skrevet ennå.

Claude foreslår at denne siden bør dekke:

- Forutsetningene: brukervilkårene er godtatt, og ROS- og personvernvurdering er gjennomført
- Be Dataspeilet om OIDC-oppsett og application ID for service principalen `<workspace>-gha-deploy`
- Opprette GitHub-miljøene `stage` og `prod` med `DATABRICKS_HOST` og `DATABRICKS_CLIENT_ID`
- Skrive workflowen: validering på pull request, deploy til stage og prod
- Sette `run_as` og `permissions` i bundlen
- Bekrefte at jobbene kjører i produksjonsworkspacet
