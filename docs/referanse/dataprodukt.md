---
title: Definisjon av dataprodukt
description: RFC for felles definisjon, minstekrav og metadata-modell for dataprodukt i Digitaliseringsetaten.
diataxis: reference
---

# Definisjon av dataprodukt

!!! info "Status: RFC (forslag)"
    Dette er et forslag (RFC) til felles definisjon og metadata-modell, ikke en
    vedtatt standard. RFC-en erstatter ikke vurderinger knyttet til
    informasjonssikkerhet, personvern, DPIA, behandlingsgrunnlag,
    databehandleravtaler, lisensiering eller juridiske vurderinger.

Et dataprodukt er en forvaltet, dokumentert og livssyklusstyrt samling av
dataressurser som tilbys for definerte formål, konsumenter eller brukstilfeller.
Det skal ha tydelig eierskap, tilgangsmodell, bruksrett, kvalitetsforventninger
og metadata som gjør produktet mulig å finne, forstå, bruke og forvalte.

**Omfang:** Teknologisk utvikling og dataforvaltning i deltakende produktområder
i Digitaliseringsetaten.

## Oversikt

- **Type:** RFC – foreslått definisjon og metadata-modell
- **Gjelder for:** Dataprodukter i Digitaliseringsetaten
- **Primærformat:** ODPS (metadata-as-code), ODCS (output-port-kontrakter)
- **Eksport / interoperabilitet:** DPROD / DCAT / DCAT-AP-NO
- **Bruksrett:** Egen modell, mappbar til ODRL

## Sammendrag

Denne RFC-en foreslår en felles definisjon, minstekrav og metadata-modell for
dataprodukt i Digitaliseringsetaten, og anbefaler denne arbeidsdelingen:

| Område | Standard / modell | Bruk |
| --- | --- | --- |
| Dataproduktmetadata | ODPS | Primært operasjonelt format / metadata-as-code |
| Output-port-kontrakter | ODCS | Kontrakter for skjema, kvalitet, SLA/SLO og endringer |
| Katalog og interoperabilitet | DPROD / DCAT / DCAT-AP-NO | Eksport, mapping og fødererte metadataøkosystemer |
| Bruksrett | Egen modell, mappbar til ODRL | Tillatt bruk, forbud, plikter, kopiering, viderebruk og KI-bruk |

Modellen skal kunne representeres i eller mappes til OpenMetadata, Microsoft
Purview, Databricks og Snowflake.

## Problemstilling

Dataressurser kan være teknisk tilgjengelige, men likevel vanskelige å bruke på
tvers av team når det mangler felles beskrivelse av:

- hva dataene skal brukes til
- hvem som eier og forvalter dem
- hvilke dataressurser, output-porter og kontrakter som inngår
- hvordan konsumenter får tilgang
- hva konsumenter har lov til å bruke dataene til etter at tilgang er gitt
- hvilke kvalitets-, ferskhets- og stabilitetsforventninger som gjelder
- hvilke regler, klassifiseringer og begrensninger som gjelder
- hvordan produktet kan representeres i kataloger og åpne standarder

Uten en felles modell øker risikoen for dobbeltarbeid, feil bruk av data, svak
sporbarhet, uklare ansvarslinjer, uklare bruksrettigheter og plattformspesifikke
løsninger.

## Mål

RFC-en skal etablere en felles praksis som gir:

- tydelig eierskap og ansvar
- bedre datakvalitet og mer forutsigbar bruk
- en metadata-modell som kan brukes på tvers av verktøy
- kompatibilitet med OpenMetadata, Microsoft Purview, Databricks, Snowflake, ODPS, ODCS og DCAT/DPROD
- bedre grunnlag for tilgangsstyring, dokumentasjon, sikkerhet, personvern, juridiske vurderinger og livssyklusforvaltning
- enklere eksport til DCAT-kompatible kataloger, for eksempel data.norge.no

## Ikke-mål

RFC-en bestemmer ikke:

- hvilken katalogløsning Digitaliseringsetaten skal bruke som primær katalog
- at alle eksisterende tabeller, API-er, rapporter eller datasett umiddelbart skal gjøres om til dataprodukter
- én bestemt teknisk implementasjon for Databricks, Snowflake, Purview eller OpenMetadata
- at DPROD skal være primært forfatterformat

## Forslag

Digitaliseringsetaten innfører dataprodukt som felles begrep og metadata-modell
for data som tilbys for gjenbruk utenfor et teams interne implementasjonsløp.

Et dataprodukt **SKAL** ha:

- stabil identitet
- navn, beskrivelse, formål og primære bruksområder
- domene eller produktområde
- dataprodukteier, dataforvalter og teknisk kontakt
- livssyklusstatus
- tilknyttede dataressurser
- minst én output-port eller tilgangsflate
- tilgangsmodell, dataklassifisering og bruksrett
- forventninger til kvalitet, ferskhet og stabilitet
- versjonering, endringspolicy og relevante referanser
- veiledning for hvordan konsumenter kobler seg på produktet

Et dataprodukt **BØR** ha ODPS-representasjon, ODCS-kontrakter for viktige
output-porter, lineage, eksempler på bruk, kjente begrensninger, SLA/SLO,
datakvalitetsmålinger, supportkontakt og maskinlesbar DCAT/DPROD-eksport der det
er relevant.

Et dataprodukt **KAN** bestå av tabeller, views, filer, API-er, strømme-topics,
rapporter, dashboards, maskinlæringsmodeller, notebooks, datadelinger, Snowflake
shares/listings, Databricks Delta Sharing shares/listings eller andre
dataressurser som er relevante for formålet.

### Minstekrav til metadata

| Felt | Krav | Beskrivelse |
| --- | --- | --- |
| `id` | SKAL | Stabil og globalt unik identifikator, helst URI/URN |
| `name` | SKAL | Kort teknisk navn |
| `title` | SKAL | Lesbart navn |
| `description` | SKAL | Hva produktet inneholder |
| `purpose` | SKAL | Hvorfor produktet finnes og hva det skal brukes til |
| `domain` | SKAL | Domene, produktområde eller organisatorisk eierskap |
| `owner` | SKAL | Ansvar for verdi, kvalitet og livssyklus |
| `dataSteward` | SKAL | Løpende forvaltning, kvalitet og brukerstøtte |
| `technicalOwner` | SKAL | Teknisk ansvarlig team eller kontaktpunkt |
| `lifecycleStatus` | SKAL | draft, development, published, deprecated eller retired |
| `assets` | SKAL | Underliggende dataressurser |
| `outputPorts` | SKAL | Hvordan konsumenter får tilgang |
| `accessPolicy` | SKAL | Hvordan tilgang gis og hvem som godkjenner |
| `usageRights` | SKAL | Hva dataene kan brukes til etter at tilgang er gitt |
| `classification` | SKAL | Sensitivitet, personopplysninger, skjerming og tilgangsnivå |
| `version` | SKAL | Versjon av dataproduktet eller output-porten |
| `inputPorts` | BØR | Hvor data kommer inn |
| `useCases` | BØR | Konkrete brukstilfeller |
| `howToConnect` | BØR | Veiledning for tilkobling og bruk |
| `contracts` | BØR | ODCS-kontrakter for output-porter |
| `quality` | BØR | Ferskhet, kompletthet, tester og kjente avvik |
| `schema` | BØR | Skjema, kontrakt eller informasjonsmodell |
| `changePolicy` | BØR | Hvordan breaking changes varsles og håndteres |
| `glossaryTerms` | BØR | Begreper som forklarer innholdet |
| `lineage` | BØR | Oppstrøms og nedstrøms avhengigheter |
| `odps` | BØR | ODPS-representasjon |
| `dcat` | BØR | Metadata for DCAT/DPROD/DCAT-AP-NO-eksport |
| `odrl` | BØR | Maskinlesbar policy for bruksrett |

### Standardvalg

Digitaliseringsetaten **BØR** bruke ODPS – Open Data Product Standard som
primært maskinlesbart format for dataproduktmetadata.

Digitaliseringsetaten **BØR** bruke ODCS – Open Data Contract Standard som
anbefalt kontraktformat for output-porter.

Digitaliseringsetaten **BØR** støtte eksport eller mapping til
DPROD/DCAT/DCAT-AP-NO der dataprodukter, datasett eller datatjenester skal inngå
i DCAT-kompatible kataloger, offentlige kataloger eller andre fødererte
metadataøkosystemer.

!!! note "DPROD i beta"
    DPROD er særlig relevant for RDF/Linked Data, semantisk interoperabilitet og
    offentlig sektor-integrasjoner. Siden DPROD 1.0 Beta 1 er i finaliseringsfase,
    BØR implementasjoner tåle endringer i standarden.

## Livssyklus og endringer

Et dataprodukt **SKAL** ha én av følgende statuser:

- `draft` – produktet er under vurdering
- `development` – produktet bygges
- `published` – produktet er tilgjengelig for konsumenter
- `deprecated` – produktet er tilgjengelig, men skal fases ut
- `retired` – produktet er ikke lenger tilgjengelig

Endring fra `published` til `deprecated` SKAL beskrive erstatning, frist og
konsekvens for konsumenter.

Breaking changes SKAL dokumenteres og BØR håndteres med ny major-versjon, ny
output-port, oppdatert kontrakt, forhåndsvarsel og/eller overgangsperiode.
Eksempler er fjerning av felt, datatypeendring, endret semantikk, endret
tilgangsmodell, endret bruksrett, endret oppdateringsfrekvens eller fjerning av
output-port.

## Assets, katalog og plattform

Tekniske assets er de fysiske dataobjektene som inngår i et dataprodukt. De kan
for eksempel organiseres slik:

```text
System
  └── Database
        └── Table
              └── Datasett
```

Metadata-modellen skiller mellom:

| Lag | Innhold | Formål |
| --- | --- | --- |
| Datakatalog | Dataprodukter, bruksrett, business assets, roller | Styring, oppdagelse og bruk |
| Dataplattform | System, Database, Table, Datasett, teknisk tilgangskontroll | Teknisk lagring og tilgang |

`accessPolicy` binder lagene sammen ved å oversette bruksrett og godkjenningsregler
til faktisk teknisk tilgang på dataplattformen.

Business assets som use cases, tilkoblingsveiledning, domene og datakvalitet
representeres gjennom henholdsvis `useCases`, `howToConnect`, `domain` og `quality`.

## Output-porter

Et dataprodukt **SKAL** ha minst én output-port. En output-port beskriver hvordan
dataproduktet tilbys til konsumenter, for eksempel SQL-tabell/view, API,
fil-distribusjon, Delta Sharing share, Snowflake share/listing, Kafka-topic,
Power BI-rapport, maskinlæringsmodell eller notebook.

En output-port **BØR** ha ODCS-kontrakt når konsumenter er avhengige av stabilt
skjema, oppdateringsfrekvens, datakvalitet, SLA/SLO, semantikk, teknisk
tilgangsinformasjon eller endringsvarsel.

Output-porter med personopplysninger, høy kritikalitet, eksplisitte SLA/SLO-er
eller stor breaking-change-risiko **SKAL** ha kontrakt eller tilsvarende
dokumentert avtale.

```yaml
outputPorts:
  - id: pxweb-table-v1
    title: Statistikkbanken tabellvisning for OK-BEF008
    type: web
    platform: pxweb
    assetRef: pxweb:statistikkbanken:db1:befolkning:folkemengde:OK-BEF008
    usageRightsRef: policies/usage/folkemengde-oslo-kristiania-apen-bruk.yaml
```

## Bruksrett

Bruksrett beskriver hva en konsument har lov til å gjøre med et dataprodukt eller
en output-port etter at tilgang er gitt. Bruksrett er ikke det samme som teknisk
tilgang:

- `accessPolicy` beskriver hvordan tilgang forespørres, godkjennes og gis
- `usageRights` beskriver hva dataene kan brukes til etter at tilgang er gitt

Et dataprodukt **SKAL** ha bruksrett dokumentert. For åpne data kan dette være
lisens og attribusjonskrav. For interne eller begrensede data kan det være
tillatt bruk, forbudt bruk, plikter, kopiering, viderebruk, KI-bruk, lagringstid
og eventuell ekstern deling.

Bruksrett **SKAL** dokumenteres særskilt når data deles på tvers av team eller
organisatoriske enheter, inneholder personopplysninger, er interne/skjermede,
kan kopieres eller eksporteres, kan brukes til KI/ML eller automatiserte
beslutninger, kan deles med tredjeparter eller publiseres eksternt.

Bruksrett erstatter ikke juridiske vurderinger, DPIA, behandlingsgrunnlag,
databehandleravtaler eller informasjonssikkerhetsvurderinger. Slike dokumenter
bør refereres fra `legalAssessmentRef` og `riskAssessmentRef` der de finnes.

Bruksrett **SKAL** kunne uttrykke:

| Attributt | Felt |
| --- | --- |
| Juridisk vurdering / DPIA | `basis.legalAssessmentRef` |
| ROS / risikovurdering | `basis.riskAssessmentRef` |
| Datakilde | `basis.source` |
| Klassifisering | `basis.classificationRef` |
| PII-informasjon | `basis.containsPersonalDataRef` |
| Tjenestekatalog | `basis.serviceCatalogRef` |
| Tillatt bruk | `permittedUses` |
| Forbudt bruk | `prohibitedUses` |
| AI-bruk | `aiUse` |
| Eksponering | `audience` |
| Ekstern deling | `externalSharing` |
| Plikter | `obligations` |
| Kopiering og viderebruk | `copyPolicy` |
| Formål | `purpose` |
| Oppbevaring | `retention` |
| Juridiske vilkår | `legal` |
| Maskinlesbar policy | `policyExpression` |

Der bruksrett skal være maskinlesbar, **BØR** ODRL vurderes som policyformat.
ODRL BØR ikke være obligatorisk i første fase, men `usageRights` BØR kunne mappes
til ODRL.

## Kompatibilitet

### OpenMetadata

Dataproduktmodellen **SKAL** kunne mappes til OpenMetadata sin Data
Product-entitet, inkludert domene, eierskap, input/output-porter og dataressurser.

| RFC-felt | OpenMetadata |
| --- | --- |
| `domain` | Domain |
| `id` / `name` | Data Product FQN eller ekstern identifikator |
| `owner` | Owner |
| `technicalOwner` | Expert eller Team |
| `assets` | Data Product assets |
| `inputPorts` / `outputPorts` | Ports eller relaterte assets |
| `contracts` | Lenker, custom properties eller relaterte ressurser |
| `usageRights` | Tags, custom properties, policy-lenker eller glossary terms |
| `classification` | Tags / Classifications |
| `quality` | Test Suites / Test Cases |

### Microsoft Purview

Dataproduktmodellen **SKAL** kunne mappes til Microsoft Purview Unified Catalog,
der dataprodukter grupperer dataressurser for et bestemt formål.

| RFC-felt | Purview |
| --- | --- |
| `domain` | Governance Domain |
| `owner` | Data Product Owner |
| `assets` | Associated Data Assets |
| `accessPolicy` | Data Product Access Policy |
| `usageRights` | Access policy metadata, terms of use eller custom metadata |
| `contracts` | Relaterte dokumenter eller custom metadata |
| `glossaryTerms` | Glossary Terms |
| `classification` | Terms, policies eller custom metadata |
| `purpose` / `useCases` | Description and use cases |
| `quality` | Data quality rules/scans der tilgjengelig |

### Databricks og Snowflake

Modellen **SKAL** kunne representere Databricks- og Snowflake-ressurser uten å
låse dataproduktet til én plattform.

| RFC-felt | Databricks | Snowflake |
| --- | --- | --- |
| `assets` | UC tables, views, volumes, models eller functions | Databases, schemas, tables, views, dynamic tables, stages eller apps |
| `outputPorts` | UC object, Delta Sharing share eller Marketplace listing | Share, listing, organizational listing eller secure view |
| `contracts` | ODCS-referanse i Git, workspace, volume eller katalog | ODCS-referanse i Git, stage, katalog eller dokument |
| `accessPolicy` | UC privileges, row/column filters eller policies | RBAC, masking policies, row access policies |
| `usageRights` | Tags, table properties og policyreferanser | Object tags, governance policies, listing terms eller metadatareferanser |
| `classification` | Tags / classifications | Object tags |
| `lineage` | Unity Catalog lineage | Snowflake lineage eller OpenLineage |
| `dataProductId` | Tag eller property på UC-objekter | Tag eller metadatafelt på relevante objekter |

### ODPS, ODCS og DCAT

Dataproduktmodellen **BØR** kunne beskrives som ODPS eller eksporteres til ODPS
fra valgt katalog/API.

| RFC-felt | Standard |
| --- | --- |
| DataProduct | ODPS data product |
| `metadata.id` | ODPS produktidentifikator |
| `ownership` | ODPS team/ownership/support |
| `purpose` | ODPS value/use case/purpose der støttet |
| `outputPorts.contractRef` | ODCS-kontrakt |
| `contracts` | Liste over ODCS-kontrakter |
| `usageRights` | ODPS terms, pricing, license, access eller extension |
| `assets` | ODPS/ODCS resource/server/infrastructure-referanser |
| `dcat` | Mapping til DPROD/DCAT-AP-NO |

For offentlige data og datatjenester **BØR** DCAT-AP-NO v3 brukes der metadata
skal inngå i norske katalogsammenhenger.

## Foreslått metadatafil

Dataprodukter **BØR** kunne beskrives maskinlesbart i `dataproduct.yaml` eller i
et tilsvarende katalog-API. Eksemplet bruker Statistikkbanken-tabellen OK-BEF008,
"Folkemengden i Oslo/Kristiania, antall personer og årlig endring, 1801-2026".
Det viser en DIG-profil som kan mappes til ODPS, ODCS og DPROD/DCAT. Dersom ODPS
velges som direkte forfatterformat, BØR feltnavn normaliseres mot ODPS-skjemaet.

```yaml
apiVersion: dig.oslo/v1alpha1
kind: DataProduct

metadata:
  id: urn:oslo:dataprodukt:befolkning:folkemengde-oslo-kristiania
  name: folkemengde-oslo-kristiania
  title:
    nb: Folkemengden i Oslo/Kristiania
  description:
    nb: Historisk folkemengde og årlig endring for Oslo/Kristiania, 1801-2026.
  domain: befolkning
  lifecycleStatus: published
  version: "2026-04-17"
  sourceTable: OK-BEF008

standards:
  primary: ODPS
  contracts: ODCS
  exportProfiles:
    - DPROD
    - DCAT-AP-NO

ownership:
  owner:
    orgUnit: Byrådsavdeling for finans
    email: oslostatistikken@example.org
  dataSteward:
    orgUnit: Oslostatistikken
    email: oslostatistikken@example.org
  technicalOwner:
    system: Statistikkbanken / PxWeb

purpose:
  summary:
    nb: Gjøre offisiell tidsserie for folkemengden i Oslo/Kristiania tilgjengelig for analyse, planlegging og rapportering.
  useCases:
    - Befolkningsanalyse
    - Historiske tidsserier
    - Planlegging
    - Rapportering
  notFor:
    - Automatiserte beslutninger om enkeltpersoner
    - Individoppfølging

howToConnect:
  steps:
    - Åpne tabellen i Statistikkbanken
    - Velg år og geografisk område
    - Last ned resultat eller bruk PxWeb API for tabell OK-BEF008

classification:
  containsPersonalData: false
  sensitivity: public
  accessRights: public
  legalBasis: not_applicable
  dataRetention: permanent

accessPolicy:
  requestUrl: https://statistikkbanken.oslo.kommune.no/statbank/pxweb/no/db1/db1__Befolkning__Folkemengde/OK-BEF008.px/
  approvalRequired: false
  accessLevel: open

usageRights:
  id: urn:oslo:bruksrett:befolkning:folkemengde-oslo-kristiania:apen-bruk
  permittedUses:
    - analysis
    - reporting
    - research
    - public_communication
  prohibitedUses:
    - automated_individual_decision_making
  aiUse:
    allowed: true
    conditions:
      - use_only_as_aggregate_statistics
  copyPolicy:
    localCopiesAllowed: true
    onwardSharingAllowed: true
    exportAllowed: true
  obligations:
    - cite_source_when_published

assets:
  - id: pxweb:statistikkbanken:db1:befolkning:folkemengde:OK-BEF008
    platform: pxweb
    type: statistical_table
    title: BEF008
    ref: https://statistikkbanken.oslo.kommune.no/statbank/pxweb/no/db1/db1__Befolkning__Folkemengde/OK-BEF008.px/
    variables:
      - år
      - geografisk område

outputPorts:
  - id: pxweb-table-v1
    title: Statistikkbanken tabellvisning
    type: web
    platform: pxweb
    endpointRef: https://statistikkbanken.oslo.kommune.no/statbank/pxweb/no/db1/db1__Befolkning__Folkemengde/OK-BEF008.px/
    usageRightsRef: policies/usage/folkemengde-oslo-kristiania-apen-bruk.yaml
    freshness:
      lastUpdated: 2026-04-17
      updateFrequency: annual

  - id: pxweb-api-v1
    title: PxWeb API for OK-BEF008
    type: api
    platform: pxweb
    endpointRef: PxWeb API for tabell OK-BEF008
    usageRightsRef: policies/usage/folkemengde-oslo-kristiania-apen-bruk.yaml

contracts:
  - id: pxweb-api-v1-contract
    standard: ODCS
    version: "3.1.0"
    appliesToOutputPort: pxweb-api-v1
    path: contracts/folkemengde-oslo-kristiania-pxweb-api.odcs.yaml

quality:
  unit: Personer
  latestUpdate: 2026-04-17
  coverage:
    timePeriod: 1801-2026
    geography:
      - Oslo
      - Kristiania
  notes:
    - Tall til og med 1970 er hentet fra folketellingene.
    - Fra og med 1980 er folkemengde oppgitt per 1. januar.

changePolicy:
  compatibility: backward
  breakingChangeNotice: P30D
  deprecationNotice: P90D

lineage:
  upstream:
    - urn:oslo:kilde:folkeregisteret
    - urn:oslo:kilde:folketellinger

odps:
  exportable: true

dcat:
  exportable: true
  profiles:
    - dcat-ap-no
    - dprod
  publisher: Oslo kommune
  theme:
    - befolkning
```

## Forvaltning

Hvert dataprodukt **SKAL** ha en dataprodukteier, en dataforvalter og en teknisk
eier. Rollene kan kombineres i små produkter, men ansvar skal være eksplisitt.

| Rolle | Ansvar |
| --- | --- |
| Dataprodukteier | Formål, verdi, kvalitet, livssyklus, tilgangsmodell, bruksrett, klassifisering, kontraktkrav og varsling ved vesentlige endringer |
| Dataforvalter | Løpende forvaltning, datakvalitet, avvik, brukerstøtte, begreper, dokumentasjon og praktisk etterlevelse av bruksrett |
| Teknisk eier | Implementasjon, drift, feilretting, skjemaendringer, overvåking, datakvalitetstester og kobling til plattformressurser |

Arkitekter og sikkerhets-/personvernressurser **BØR** involveres når dataproduktet
inneholder personopplysninger eller sensitiv informasjon, deles eksternt eller på
tvers av organisatoriske grenser, brukes til automatiserte beslutninger/KI, har
stor konsekvens ved feil eller har uklar juridisk ramme.

## Publisering

Et dataprodukt regnes som publisert når:

- metadata er komplett etter minstekravene
- minst én output-port er tilgjengelig eller kan forespørres
- eierskap, tilgangsmodell, bruksrett og klassifisering er avklart
- kvalitetsforventninger er dokumentert
- kontrakt finnes for output-porter der dette er påkrevd
- produktet er synlig i valgt katalog eller felles oversikt
- ODPS- og DCAT/DPROD-eksport kan genereres der det er relevant

## Suksesskriterier

RFC-en anses som vellykket dersom:

- nye dataprodukter kan beskrives med samme minimumsmodell
- modellen kan mappes til OpenMetadata og Microsoft Purview uten vesentlig informasjonstap
- modellen kan beskrives eller eksporteres som ODPS
- output-porter kan knyttes til ODCS-kontrakter der det er relevant
- Databricks- og Snowflake-ressurser kan kobles til dataprodukter via stabil identitet
- dataprodukter kan eksponeres som DCAT/DPROD-kompatible metadata der det er relevant
- bruksrett kan dokumenteres tydelig og skilles fra teknisk tilgang
- konsumenter kan finne eier, formål, tilgangsmåte, bruksrett og kvalitet uten å kjenne underliggende plattform
- modellen piloteres på minst ett dataprodukt fra to ulike domener

## Konsekvenser

**Fordeler:**

- bedre gjenbruk av data
- tydeligere eierskap
- tydeligere skille mellom tilgang og tillatt bruk
- mindre plattforminnlåsing
- enklere katalogisering og datadeling
- bedre samsvar med offentlig sektor-standarder
- enklere integrasjon mellom OpenMetadata, Purview, Databricks og Snowflake
- bedre grunnlag for kontrollert KI-bruk, viderebruk og ekstern deling

**Ulemper:**

- team må vedlikeholde mer metadata
- output-porter kan kreve egne kontrakter
- bruksrett må avklares og holdes oppdatert
- validering og synkronisering mellom systemer må etableres
- eksisterende dataressurser må migreres gradvis
- DPROD er fortsatt i beta
- ODPS/ODCS-mapping må tilpasses praktisk verktøystøtte

## Implementeringsforslag

1. Enighet om begrep, minimumsmodell og ODPS som primært operasjonelt format
2. Pilot med 2–3 dataprodukter i ulike team
3. Maler for `dataproduct.yaml`, ODCS-kontrakter og bruksrett
4. Validering av metadatafil, kontrakter og katalogmapping
5. Mapping mot OpenMetadata, Purview, Databricks og Snowflake
6. Eksport til DPROD/DCAT-AP-NO der relevant
7. Beslutning om primær katalog og synkroniseringsmønster
8. Gradvis innføring for nye dataprodukter

## Åpne spørsmål

- Skal `dataproduct.yaml` være obligatorisk, eller holder det at metadata finnes i en katalog?
- Skal ODPS være obligatorisk for alle nye dataprodukter, eller holder det at valgt katalog kan eksportere ODPS?
- Skal ODCS være obligatorisk for alle output-porter, eller bare for publiserte/gjenbrukte output-porter?
- Skal DPROD/DCAT-AP-NO være obligatorisk eksportprofil for alle dataprodukter, eller bare for dataprodukter i offentlig katalogsammenheng?
- Hvilke metadatafelt skal være obligatoriske for interne dataprodukter versus eksternt delte dataprodukter?
- Hvordan skal tilgangsforespørsler og bruksrett håndteres på tvers av Databricks, Snowflake og Purview?
- Skal bruksrett dokumenteres på dataproduktnivå, output-port-nivå eller begge deler?
- Hvilke bruksformål skal være standardvalg?
- Skal KI-trening være forbudt som standard med eksplisitt godkjenning?
- Skal ODRL brukes som maskinlesbart policyformat, eller er YAML-felt tilstrekkelig i første fase?

## Anbefaling

Digitaliseringsetaten bør innføre dataprodukt som felles begrep og bruke
metadata-modellen i denne RFC-en som minimumsstandard.

ODPS bør være primært operasjonelt format. ODCS bør brukes for output-porter som
trenger eksplisitte kontrakter. DPROD/DCAT-AP-NO bør støttes som eksport- og
interoperabilitetsprofil.

Bruksrett bør være et obligatorisk metadataområde, adskilt fra teknisk
tilgangsstyring. Der maskinlesbar policy er nødvendig, bør bruksrett kunne
uttrykkes eller mappes til ODRL.

## Referanser

1. Open Data Product Standard (ODPS)
2. Open Data Contract Standard (ODCS)
3. OMG DPROD 1.0 Beta 1
4. W3C DCAT v3
5. DCAT-AP-NO v3
6. W3C ODRL Information Model
7. W3C ODRL Vocabulary
8. OpenMetadata Data Products
9. Microsoft Purview Data Products
10. Microsoft Purview – Create and Manage Data Products
11. Microsoft Purview – Data Product Access Policies
12. Databricks Unity Catalog
13. Databricks Delta Sharing and Marketplace
14. Snowflake Horizon Catalog and Listings
15. Snowflake Listings
16. Statistikkbanken OK-BEF008

## Relatert innhold

**Forklaringer:**

- [Hva er et dataprodukt](../om-plattformen/konsepter/dataprodukter.md)

**Referanse:**

- [Roller og rettigheter](roller-og-rettigheter.md)
- [Datakvalitet](datakvalitet.md)
- [Navnekonvensjoner](navnekonvensjoner.md)
