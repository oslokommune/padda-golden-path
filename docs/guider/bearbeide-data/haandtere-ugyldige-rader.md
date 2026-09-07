---
title: Håndtere rader som ikke lar seg konvertere
description: Hvordan konvertere typer robust og sette ugyldige rader i karantene i stedet for å stoppe pipelinen.
diataxis: how-to
icon: lucide/construction
---

# Håndtere rader som ikke lar seg konvertere

Denne guiden er ikke skrevet ennå.

Claude foreslår at denne siden bør dekke:

- `try_cast` og eksplisitte datoformater i stedet for `CAST`
- Skille ugyldige rader ut i en egen karantenetabell med expectations
- Når `NOT NULL` bør stoppe pipelinen, og når en expectation er riktigere
- Finne raden i bronze som stoppet oppdateringa når `NOT NULL` slår til
- Følge opp karantenetabellen: varsling og retting i kilden
