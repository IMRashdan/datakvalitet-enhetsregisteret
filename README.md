# Datakvalitet i Enhetsregisteret

![Tester](https://github.com/BRUKERNAVN/datakvalitet-enhetsregisteret/actions/workflows/tester.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![DuckDB](https://img.shields.io/badge/DuckDB-SQL-yellow)

Systematisk kartlegging av datakvalitet i Enhetsregisteret basert på åpne data fra
Brønnøysundregistrene. Prosjektet kombinerer profilering, regelbaserte kontroller og
sammenstilling med en ekstern kilde (Postens postnummerregister), og resultatene
lagres slik at kvaliteten kan følges over tid.

> **Hovedfunn:** Enhetsregisteret har svært høy kvalitet på identifikatorer og formater. Avvikene utgjør under 0,2 % og følger forklarbare mønstre: 81 % av aksjeselskapene uten næringskode er nyregistrerte, og alle 459 poststedsavvik skyldes ett postnummer. Se [funnotatet](docs/funnotat.md).

## Problemstilling

Hvor god er kvaliteten på dataene i Enhetsregisteret, hvor ligger eventuelle svakheter,
og hva er sannsynlige årsaker? Målet er ikke bare å telle feil, men å forstå *hvorfor*
tallene ser ut som de gjør og foreslå tiltak.

## Metode

Kontrollene er organisert etter fire vanlige datakvalitetsdimensjoner:

| Dimensjon | Spørsmål | Eksempel på kontroll |
|---|---|---|
| **Kompletthet** | Finnes verdien der den forventes? | Aksjeselskap uten næringskode |
| **Gyldighet** | Følger verdien formatet og reglene? | Mod11-kontroll av organisasjonsnummer |
| **Konsistens** | Henger verdiene sammen, internt og mot andre kilder? | Postnummer og poststed mot Postens register |
| **Unikhet** | Finnes det duplikater? | Ulike enheter med samme navn og postnummer |

mod11-kontrollen og duplikatkontrollene er skrevet i SQL og kjører inne i DuckDB, slik at
alle 1,2 millioner enheter kontrolleres på noen sekunder. En egen test sikrer at SQL-versjonen
av mod11 gir samme svar som Python-versjonen.

Hver kontroll er definert som data (en *populasjon* og et *avvikskriterium* i SQL) i
[`src/dq/kontroller.py`](src/dq/kontroller.py). Nye kontroller legges til uten å endre
kjøremotoren, og kontroller som mangler nødvendige kolonner eller tabeller hoppes over
med en forklaring i stedet for å feile.

Rådata leses inn som tekst (`all_varchar`), slik at ingen verdier stilles «reparert» av
automatisk typetolkning før de er kontrollert.

## Kontroller

| ID | Kontroll | Dimensjon |
|---|---|---|
| G01 | Gyldig organisasjonsnummer (mod11) | Gyldighet |
| G02 | Postnummer har fire sifre | Gyldighet |
| G03 | Gyldig format på næringskode | Gyldighet |
| G04 | Stiftelsesdato er ikke i fremtiden | Gyldighet |
| K01 | Forretningsadresse har postnummer | Kompletthet |
| K02 | Aksjeselskap har næringskode | Kompletthet |
| S01 | Stiftet før registrering | Konsistens |
| S02 | Antall ansatte samsvarer med registrert ansattforhold | Konsistens |
| S03 | Postnummer finnes i Postens register | Konsistens |
| S04 | Poststed samsvarer med postnummer | Konsistens |
| U01 | Unikt organisasjonsnummer | Unikhet |
| U02 | Mulige duplikater (navn + postnummer) | Unikhet |

## Kom i gang

```bash
git clone https://github.com/BRUKERNAVN/datakvalitet-enhetsregisteret.git
cd datakvalitet-enhetsregisteret
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

python -m dq.kjor last-ned     # laster ned Enhetsregisteret (CSV, gzip)
python -m dq.kjor kolonner     # viser kolonnene etter normalisering
python -m dq.kjor kontroller   # kjører kontrollene og skriver rapport
```

**Valgfritt:** Last ned Postens postnummerregister (tabulatorseparert tekstfil) fra
[Bring](https://www.bring.no/tjenester/adressetjenester/postnummer) og lagre den som
`data/raw/postnummer.txt` for å aktivere kontrollene S03 og S04.

Resultatene skrives til `resultater/kvalitetsrapport.md` og `resultater/kontrollresultater.csv`,
og hver kjøring lagres i tabellen `kvalitetsresultat` i DuckDB-databasen.

## Struktur

```
├── src/dq/
│   ├── orgnr.py          # mod11-validering av organisasjonsnummer
│   ├── database.py       # innlasting til DuckDB og normalisering av kolonnenavn
│   ├── kontroller.py     # kontrolldefinisjoner og kjøremotor
│   ├── profilering.py    # kompletthet per kolonne
│   ├── rapport.py        # Markdown- og CSV-rapport
│   ├── last_ned.py       # nedlasting fra data.brreg.no
│   └── kjor.py           # kommandolinje
├── sql/profilering.sql   # utforskende spørringer
├── tests/                # pytest med konstruerte testdata
├── utforskning/          # skript brukt til å undersøke årsakene bak avvikene
├── docs/funnotat.md      # funn og anbefalinger til dataeier
└── resultater/           # kvalitetsrapport fra kjøring på ekte data
```

## Testing

```bash
pytest -v
```

Testdataene i `tests/fixtures/` er konstruert slik at hver rad trigger én kjent feil.
Testene dokumenterer dermed samtidig hva hver kontroll fanger opp. Testene kjøres
automatisk med GitHub Actions ved hver push.

## Begrensninger

- Analysen bruker kun åpne data, så skjermede opplysninger er ikke med.
- Enkelte kontroller (særlig U02) gir kandidater for manuell vurdering, ikke bekreftede feil.
- Et avvik kan skyldes regelverk eller historisk praksis og trenger ikke bety feil i registeret.

## Datakilder

- [Enhetsregisteret, åpne data](https://data.brreg.no/enhetsregisteret/api/dokumentasjon/no/index.html), Brønnøysundregistrene (NLOD)
- Postnummerregister, Posten/Bring
