---
title: Lagring og ytelse
description: Hvordan optimalisere den lagrede dataen for kostnad og ytelse.
diataxis: how-to
---

# Lagring og ytelse

Skrives de resulterende tabellene oftere enn de leses? Er de små (<1TB)? Da er det sannsynligvis godt nok å bruke standardinnstillingene (med mindre lagringskostnadene blir et problem). Hvis begge disse er usanne, finnes det noen interessante alternativer for hvordan du grupperer data på disk:

- [Liquid Clustering](https://docs.databricks.com/aws/en/delta/clustering): Databricks håndterer dette selv. Dette anbefales av Databricks og er sannsynligvis et godt valg i de fleste tilfeller.
- [Partisjonering](https://docs.databricks.com/aws/en/tables/partitions): Hvis du har en kolonne med få (hundrevis av) distinkte verdier som du vet vil dukke opp i en WHERE-klausul i de fleste spørringer, er dette alternativet for deg. Advarsel: Ikke lett å reversere.
- [Z-ordering](https://docs.databricks.com/aws/en/delta/data-skipping): Lar beregningsressursene hoppe over visse parquet-filer under spørringer basert på statistikk, og kan gi bedre komprimering.

Et annet spørsmål er prediktiv optimalisering kontra eksplisitt kjøring av VACUUM og OPTIMIZE. Erfaring i felt med prediktiv optimalisering har vært litt blandet. Det kan være bedre å kjøre disse eksplisitt daglig.

Til slutt, på inntakssiden – hvis antallet inndatafiler blir tilstrekkelig stort, kan det være verdt å vurdere å bruke filvarslinger. I skrivende stund tillater dessverre ikke infrastrukturkonfigurasjonen vår dette, men det kan endres ved behov.
