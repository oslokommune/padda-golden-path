---
title: Sette opp Slack-alarmer
description: Hvordan sette opp Slack-varsler for Databricks-jobber med notification destinations.
diataxis: how-to
---

# Slack-varsler

Slack-varsler kan settes opp i bundle.

Lagre Slack-webhooken i en Databricks secret scope (for eksempel dataspeilet/slack-webhook).
Opprett en notification destination (krever workspaceadmin) som peker til hemmeligheten:

```bash
databricks notification-destinations create --json '{
  "display_name": "slack-dev-alerts",
  "config": {
    "slack": {
      "url": "{{secrets/dataspeilet/slack-webhook}}"
    }
  }
}'
```

Hent ID-en med:
```bash
databricks notification-destinations list
```
og sett `alert_notification_id` før du deployer.
