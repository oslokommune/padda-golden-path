---
title: Lagring og ytelse
description: Hvordan optimalisere den lagrede dataen for kostnad og ytelse.
diataxis: how-to
---

# Lagring og ytelse

Are the resulting tables written more often than they are read? Are they small (<1TB)? Then just using the defaults is probably good enough (unless storage cost becomes a concern). If both of those are false then there are some interesting options available to us in terms of how you group data on disk:

- Liquid Clustering: Databricks manages it. This is recommended by Databricks and probably not a bad choice in the general case.
- Partitioning: If you have a column with few (hundreds) distinct values that you know is going to be in a WHERE clause in most queries, this is the one for you. Caution: Not easy to reverse.
- Z-ordering: Lets your compute skip certain parquet files during query based on statistics and can result in better compression.

Another question is predictive optimization vs explicitly running VACUUM and OPTIMIZE. Field experience with predictive optimization has been a bit mixed. Explicitly running these daily might be better.

Lastly, on the input side if the number of input files becomes sufficiently great, then we might want to think about using file notifications, but as of the time we write this, the infrastructure config does not allow this.
