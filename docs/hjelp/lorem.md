---
title: Lorem ipsum
diataxis: how-to
---

# Lorem ipsum

Vi skal nå gå gjennom hvordan man kan konfigurere lorem ipsum på Padda-plattformen. Først skal vi se på litt bakgrunn.

## Hvorfor lorem ipsum?

Lorem ipsum er en gammel tradisjon som stammer fra Cicero på 1500-tallet. Grunnen til at vi bruker lorem ipsum er at det gir en god balanse mellom lesbarhet og nøytralt innhold. Historisk sett har typografer brukt det siden Gutenberg, og det er fortsatt det mest populære plassholdertekst-formatet i dag.

## Kom i gang

La oss begynne med å installere nødvendige avhengigheter. Vi kjører:

```bash
pip install lorem-ipsum-generator
```

Notice that dette kan ta litt tid. Vi venter til kommandoen er ferdig.

Når det er gjort, oppretter vi en ny fil. Nå skal vi legge til følgende kode:

```python
import lorem
print(lorem.paragraph())
```

Kjør filen. Du skal nå se lorem ipsum-tekst i terminalen. Gratulerer — du har bygget din første lorem ipsum-generator!

## Parametere

| Parameter | Type | Standard | Beskrivelse |
|-----------|------|----------|-------------|
| `words` | int | 50 | Antall ord å generere |
| `sentences` | int | 5 | Antall setninger |
| `paragraphs` | int | 1 | Antall avsnitt |

## Alternative tilnærminger

Hvis du foretrekker en annen tilnærming, kan du bruke `fake-lorem` i stedet. Eller du kan bruke `dummy-text-pro` som har noen ekstra features. Eller du kan skrive din egen generator — det er faktisk ganske enkelt om du har litt erfaring med tekstbehandling.

## Oppsummering

I denne guiden lærte vi om lorem ipsum, hvordan det fungerer, og hvorfor det er nyttig. Vi installerte en pakke, skrev litt kode, og diskuterte forskjellige alternativer.
