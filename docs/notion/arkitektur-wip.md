# Referansearkitektur
Databricks har tatt frem en referansearkitektur som ligger til grunn for alle datafløder:

Kilde: [https://docs.databricks.com/aws/en/assets/files/reference-architecture-databricks-on-aws-4f96ff7f6d8f4c112959c7f7912f55dc.pdf](https://docs.databricks.com/aws/en/assets/files/reference-architecture-databricks-on-aws-4f96ff7f6d8f4c112959c7f7912f55dc.pdf)

> ⚠️ Originalarkitekturen dekker et bredt spekter av kapasiteter. Under har vi en *revidert *arkitektur tilpasset dagens behov, med valg av komponenter, ansvarsfordeling og konkrete anbefalinger til dataproduserende team.


# TLDR - Kortversjon
Vi beholder medallion-konseptet (Landing → Bronze → Silver → Gold) implementert som Delta-tabeller i S3, administrert via Databricks og styrt gjennom Unity Catalog for policy/tilgang/lineage. Ingest og streaming håndteres gjennom Auto Loader / Lakeflow (Delta Live Tables) eller Structured Streaming; batch via jobs/Workflows og deployet gjennom DAB (Data Asset Bundle).



# DIG Databricks arkitektur
[Revidert arkitektur i Miro](https://miro.com/app/board/uXjVKMt4YVY=/)

## Hovedkomponenter
- **Storage:** Amazon S3 (objektlagring) med Delta Lake-format for alle tabeller.

- **Compute: **Databricks clusters / serverless SQL endpoints / job clusters.

- **Ingestion: **Auto Loader, Lakeflow (Delta Live Tables), Structured Streaming, Kafka/Kinesis Connectors, JDBC.

- **Catalog & governance:** Unity Catalog for katalogisering, rollebasert tilgang, auditing og grunnleggende lineage.

- **Orchestration: **Databricks Workflows / Jobs / Terraform + GitHub Actions for CI/CD.

- **Monitoring & Observability:** Databricks metrikker + CloudWatch, Datadog, Delta table metrics, job logs.

- **Serving & BI:** SQL-warehouses/Serverless endpoints (for Power BI), Delta Sharing for eksterne forbrukere.


## Detaljert oversikt for komponenter (minimert for bedre lesbarhet)

# Struktur

Git, DAB, etc

# Kilder - typer og veier inn
Kilder kan deles i filbasert og systembasert (API/db/stream). Hver kilde får et standardisert ingest-mønster


## Filbasert kilde
Typiske filer vil være csv, excel eller json men kan også inkludere parquet eller annet format.

Ved hjelp av predefinerte pipelines flyter disse videre fra landing til bronse for filer som pushes til plattformen. For filer som pulles/hentes kan det gjøres gjennom et job men filen vil da ikke gå gjennom landing sone uten direkte til bronse.

### Ad-hoc
  Filer som er for ad-hoc midlertidlig analyse eller engangs bruk kan legges inn gjennom GUI.

### Systematisert
  Filer som ikke er for midlertidlig analyse eller engang bruk settes opp for CLI


- Push til Landing via S3 opplasting (GUI/CLI)

- Auto Loader registrerer nye filer og laster til Bronse via inkrementelle streamingjobber


## Systembasert kilde (API, DB, stream)
Typiske systembaserte kilder har for push mulighet å benytte CLI for å pushe data til landing som en fil eller push som strøm. Det er også mulig at benytte API-basert enten som fil eller som strøm men da som en pull. Videre er det mulig å koble seg rett til database som batch eller strøm.

### Pull gjennom API
Bruk av pyspark custom data sources enten som batch eller stream. Defineres som Brolagt sti.


### Push gjennom CLI
Skiller seg ikke mot filbasert annet enn at det er systembruker som pusher data. defineres som Brolagt sti


### Pull gjennom strøm
Lake flow connection mot strøm definert av kildesystemet. Brolagt sti(?)


### Pull gjennom database batch og strøm
CDC strøm der mulig ellers JDBC



# Ingest
Dette prosesskrittet håndteres av dataproduserende team med føringer fra Dataspeilet men krever at Dataspeilet har satt opp tilgangsstyring.



**Landing → Bronse inkluderer**

- **Unity Catalog – External locations & storage credentials** for styrt landning‑sti i S3. Dette gir tilgangsstyring og logging fra start.

- **Auto Loader** for inkrementell filinnlasting fra S3 til Bronse‑tabeller (batch/streaming). som del av Lakeflow‑pipeline


## Pipelines
Standardpipelines/bibliotek

Lakeflow Declarative Pipelines + Auto Loader som standard “landing→bronse”

Lakeflow Jobs (Workflows) for å trigge pipeline‑oppdateringer (pipeline‑task)

Databricks Asset Bundles (CI/CD) for å versjonere pipeline‑ressurser og deploye til dev/prod

# Transform
Bronse→Sølv→Gull

Medallion brukes for gradvis raffinering; **Silver er valgfri** hvis transformasjonene ikke tilsier lagdeling.

### Tester/expectations
I Lakeflow Declarative Pipelines defineres forventninger (f.eks. `expect_or_drop`) som kan feile, droppe eller advare ved databrudd.

### Datakvalitet
Lakehouse Monitoring overvåker ferskhet/kompletthet for tabeller og gjør resultatene synlige i Catalog Explorer.


## Pipelines
Begrenset standardisering, men tvingende tester → håndhev expectations i pipelinekode (SQL/Python) og bryt på brudd.


Brolagt sti for Lakeflow Declarative Pipelines med expectations‑eksempler (mønstre for evolverende skjema, dublettkontroll osv.).

# Query/Prosess
Orkestrering

- Lakeflow Jobs (Workflows) for graf av oppgaver, planlegging, feilhåndtering og varsling – inkl. pipeline‑task.

- Databricks SQL warehouses for spørring/BI

# Serve
Delta Sharing for sikker, zero‑copy deling av data internt/eksternt – også Databricks‑til‑Databricks.

# Analyse
Analysen støttes av Unity Catalog (styring, lineage, deling) og Databricks AI/BI (Dashboards og Genie).

# Integrate

## Fabric
Shortcut
Delta lake til adslv2


## Power BI
Bruk Databricks‑connectoren mot et SQL warehouse for DirectQuery/Import og SQL‑spørringer.
