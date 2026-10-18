import time
from dataclasses import dataclass
from datetime import datetime

import duckdb

from dq.database import kolonner


@dataclass(frozen=True)
class Kontroll:
    id: str
    navn: str
    dimensjon: str          # Kompletthet | Gyldighet | Konsistens | Unikhet
    beskrivelse: str
    avvik: str              # SQL-betingelse som er sann for avvikende rader
    populasjon: str = "TRUE"  # SQL-betingelse for hvilke rader som kontrolleres
    krever_kolonner: tuple[str, ...] = ()
    krever_tabeller: tuple[str, ...] = ()


@dataclass
class Resultat:
    kontroll: Kontroll
    kontrollert: int
    avvik: int
    eksempler: list[str]

    @property
    def andel(self) -> float:
        return self.avvik / self.kontrollert if self.kontrollert else 0.0


KONTROLLER: list[Kontroll] = [
    Kontroll(
        id="G01", navn="Gyldig organisasjonsnummer", dimensjon="Gyldighet",
        beskrivelse="Organisasjonsnummeret skal ha ni sifre og korrekt mod11-kontrollsiffer.",
        avvik="NOT gyldig_orgnr(organisasjonsnummer)",
        krever_kolonner=("organisasjonsnummer",),
    ),
    Kontroll(
        id="U01", navn="Unikt organisasjonsnummer", dimensjon="Unikhet",
        beskrivelse="Hvert organisasjonsnummer skal forekomme én gang.",
        avvik="_antall_samme_orgnr > 1",
        krever_kolonner=("organisasjonsnummer",),
    ),
    Kontroll(
        id="U02", navn="Mulige duplikater (navn + postnummer)", dimensjon="Unikhet",
        beskrivelse="Flere enheter med identisk navn og forretningspostnummer. "
                    "Kan være legitimt, men bør undersøkes.",
        populasjon="navn IS NOT NULL AND forretningsadresse_postnummer IS NOT NULL",
        avvik="_antall_samme_navn_postnr > 1",
        krever_kolonner=("navn", "forretningsadresse_postnummer"),
    ),
    Kontroll(
        id="K01", navn="Forretningsadresse har postnummer", dimensjon="Kompletthet",
        beskrivelse="Enheter med forretningsadresse i Norge bør ha postnummer.",
        populasjon="coalesce(forretningsadresse_landkode, 'NO') = 'NO' "
                   "AND forretningsadresse_poststed IS NOT NULL",
        avvik="forretningsadresse_postnummer IS NULL OR trim(forretningsadresse_postnummer) = ''",
        krever_kolonner=("forretningsadresse_postnummer", "forretningsadresse_poststed",
                         "forretningsadresse_landkode"),
    ),
    Kontroll(
        id="K02", navn="Aksjeselskap har næringskode", dimensjon="Kompletthet",
        beskrivelse="Aksjeselskaper driver næringsvirksomhet og forventes å ha næringskode.",
        populasjon="organisasjonsform_kode = 'AS'",
        avvik="naeringskode1_kode IS NULL OR trim(naeringskode1_kode) = ''",
        krever_kolonner=("organisasjonsform_kode", "naeringskode1_kode"),
    ),
    Kontroll(
        id="G02", navn="Postnummer har fire sifre", dimensjon="Gyldighet",
        beskrivelse="Norske postnummer består av nøyaktig fire sifre.",
        populasjon="forretningsadresse_postnummer IS NOT NULL "
                   "AND coalesce(forretningsadresse_landkode, 'NO') = 'NO'",
        avvik="NOT regexp_full_match(forretningsadresse_postnummer, '\\d{4}')",
        krever_kolonner=("forretningsadresse_postnummer", "forretningsadresse_landkode"),
    ),
    Kontroll(
        id="G03", navn="Gyldig format på næringskode", dimensjon="Gyldighet",
        beskrivelse="Næringskoder (SN2007/SN2025) har formatet NN.NNN.",
        populasjon="naeringskode1_kode IS NOT NULL",
        avvik="NOT regexp_full_match(naeringskode1_kode, '\\d{2}\\.\\d{1,3}')",
        krever_kolonner=("naeringskode1_kode",),
    ),
    Kontroll(
        id="G04", navn="Stiftelsesdato er ikke i fremtiden", dimensjon="Gyldighet",
        beskrivelse="En enhet kan ikke være stiftet etter dagens dato.",
        populasjon="try_cast(stiftelsesdato AS DATE) IS NOT NULL",
        avvik="try_cast(stiftelsesdato AS DATE) > current_date",
        krever_kolonner=("stiftelsesdato",),
    ),
    Kontroll(
        id="S01", navn="Stiftet før registrering", dimensjon="Konsistens",
        beskrivelse="Stiftelsesdato etter registreringsdato i Enhetsregisteret er "
                    "uventet og kan tyde på feilregistrering.",
        populasjon="try_cast(stiftelsesdato AS DATE) IS NOT NULL "
                   "AND try_cast(registreringsdatoenhetsregisteret AS DATE) IS NOT NULL",
        avvik="try_cast(stiftelsesdato AS DATE) > "
              "try_cast(registreringsdatoenhetsregisteret AS DATE)",
        krever_kolonner=("stiftelsesdato", "registreringsdatoenhetsregisteret"),
    ),
    Kontroll(
        id="S02", navn="Ansatte uten registrert ansattforhold", dimensjon="Konsistens",
        beskrivelse="Antall ansatte > 0 bør samsvare med at enheten har registrerte ansatte.",
        populasjon="try_cast(antall_ansatte AS INTEGER) > 0",
        avvik="NOT coalesce(try_cast(har_registrert_antall_ansatte AS BOOLEAN), FALSE)",
        krever_kolonner=("antall_ansatte", "har_registrert_antall_ansatte"),
    ),
    Kontroll(
        id="S03", navn="Postnummer finnes i Postens register", dimensjon="Konsistens",
        beskrivelse="Postnummeret skal finnes i Postens postnummerregister (ekstern kilde).",
        populasjon="regexp_full_match(forretningsadresse_postnummer, '\\d{4}')",
        avvik="forretningsadresse_postnummer NOT IN (SELECT postnummer FROM postnummer)",
        krever_kolonner=("forretningsadresse_postnummer",),
        krever_tabeller=("postnummer",),
    ),
    Kontroll(
        id="S04", navn="Poststed samsvarer med postnummer", dimensjon="Konsistens",
        beskrivelse="Poststedet skal være det Posten oppgir for postnummeret.",
        populasjon="forretningsadresse_postnummer IN (SELECT postnummer FROM postnummer)",
        avvik="(forretningsadresse_postnummer, upper(trim(forretningsadresse_poststed))) "
              "NOT IN (SELECT (postnummer, upper(poststed)) FROM postnummer)",
        krever_kolonner=("forretningsadresse_postnummer", "forretningsadresse_poststed"),
        krever_tabeller=("postnummer",),
    ),
]


def kan_kjores(con: duckdb.DuckDBPyConnection, k: Kontroll) -> tuple[bool, str]:
    mangler = set(k.krever_kolonner) - kolonner(con, "enheter")
    if mangler:
        return False, f"mangler kolonner: {', '.join(sorted(mangler))}"
    for tabell in k.krever_tabeller:
        if not kolonner(con, tabell):
            return False, f"mangler tabell: {tabell}"
    return True, ""


def kjor_kontroll(
    con: duckdb.DuckDBPyConnection, k: Kontroll, antall_eksempler: int = 5
) -> Resultat:
    kontrollert, avvik = con.execute(
        f"SELECT count(*), count(*) FILTER (WHERE coalesce(({k.avvik}), FALSE)) "
        f"FROM enheter WHERE {k.populasjon}"
    ).fetchone()
    eksempler = [r[0] for r in con.execute(
        f"SELECT organisasjonsnummer FROM enheter WHERE ({k.populasjon}) "
        f"AND coalesce(({k.avvik}), FALSE) LIMIT {antall_eksempler}"
    ).fetchall()]
    return Resultat(k, kontrollert, avvik, eksempler)


def kjor_alle(
    con: duckdb.DuckDBPyConnection,
    kontroller: list[Kontroll] = KONTROLLER,
    vis_fremdrift: bool = False,
) -> tuple[list[Resultat], list[tuple[Kontroll, str]]]:
    resultater, hoppet_over = [], []
    for k in kontroller:
        ok, grunn = kan_kjores(con, k)
        if not ok:
            hoppet_over.append((k, grunn))
            continue
        if vis_fremdrift:
            print(f"  kjører {k.id} {k.navn} ...", end=" ", flush=True)
        start = time.perf_counter()
        resultater.append(kjor_kontroll(con, k))
        if vis_fremdrift:
            print(f"{time.perf_counter() - start:.1f} s", flush=True)
    return resultater, hoppet_over


def lagre_historikk(con: duckdb.DuckDBPyConnection, resultater: list[Resultat]) -> None:
    """Lagrer resultatene med tidsstempel, slik at kvaliteten kan følges over tid."""
    con.execute("CREATE TABLE IF NOT EXISTS kvalitetsresultat (kjoretidspunkt TIMESTAMP, "
                "kontroll_id VARCHAR, dimensjon VARCHAR, kontrollert BIGINT, avvik BIGINT)")
    na = datetime.now()
    con.executemany("INSERT INTO kvalitetsresultat VALUES (?, ?, ?, ?, ?)",
                    [(na, r.kontroll.id, r.kontroll.dimensjon, r.kontrollert, r.avvik)
                     for r in resultater])
