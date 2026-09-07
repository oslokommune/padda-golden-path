---
title: Deduplisere data i silver
description: Hvordan fjerne duplikater og beholde siste versjon av hver rad når bronze akkumulerer flere leveranser av samme data.
diataxis: how-to
icon: lucide/construction
---

# Deduplisere data i silver

Denne guiden er ikke skrevet ennå.

Claude foreslår at denne siden bør dekke:

- Skille mellom ekte duplikater og flere versjoner av samme rad (fulle snapshots i bronze)
- Beholde siste versjon per nøkkel med en vindusfunksjon i en materialisert view
- Bruke `AUTO CDC` fra snapshots når historikk skal bevares
- Hvorfor en streaming-tabell ikke kan deduplisere på tvers av kjøringer
