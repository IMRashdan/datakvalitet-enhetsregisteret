import re
from pathlib import Path

import duckdb

RAA_ENHETER = Path("data/raw/enheter.csv.gz")
RAA_POSTNUMMER = Path("data/raw/postnummer.txt")
DB_FIL = Path("data/enhetsregisteret.duckdb")

# mod11-kontroll av organisasjonsnummer skrevet som SQL-makro. Den kjører inne i
# DuckDB i stedet for å kalle Python én gang per rad, noe som er mye raskere på
# over én million rader. Python-versjonen i orgnr.py brukes til å teste at de er like.
_VEKTER = (3, 2, 7, 6, 5, 4, 3, 2)
_VEKTET_SUM = " + ".join(
    f"{v} * try_cast(substr(o, {i}, 1) AS INTEGER)" for i, v in enumerate(_VEKTER, start=1)
)
SQL_MAKROER = f"""
CREATE OR REPLACE MACRO orgnr_rest(o) AS ({_VEKTET_SUM}) % 11;
CREATE OR REPLACE MACRO gyldig_orgnr(o) AS
    coalesce(regexp_full_match(trim(o), '\\d{{9}}'), FALSE)
    AND coalesce(
        CASE orgnr_rest(trim(o)) WHEN 0 THEN 0 ELSE 11 - orgnr_rest(trim(o)) END
            = try_cast(substr(trim(o), 9, 1) AS INTEGER),
        FALSE);
"""


def normaliser_kolonnenavn(navn: str) -> str:
    """'forretningsadresse.postnummer' -> 'forretningsadresse_postnummer',
    'antallAnsatte' -> 'antall_ansatte'."""
    navn = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", navn)
    return re.sub(r"[^0-9a-z]+", "_", navn.lower()).strip("_")


def koble_til(db_fil: Path | str = DB_FIL) -> duckdb.DuckDBPyConnection:
    if str(db_fil) != ":memory:":
        Path(db_fil).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_fil))
    con.execute(SQL_MAKROER)
    return con


def last_inn_enheter(con: duckdb.DuckDBPyConnection, fil: Path | str = RAA_ENHETER) -> int:
    """Leser CSV-en (alt som tekst, så ingen verdier 'repareres' ved innlesing) rett
    inn i tabellen `enheter` med normaliserte kolonnenavn.

    I samme omgang beregnes to hjelpekolonner (prefiks _) med vindusfunksjoner,
    slik at duplikatkontrollene ikke trenger tunge delspørringer per rad.
    """
    sti = str(fil).replace("'", "''")
    kilde = f"read_csv('{sti}', header=true, all_varchar=true)"
    raa_kolonner = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {kilde}").fetchall()]
    utvalg = ", ".join(f'"{k}" AS {normaliser_kolonnenavn(k)}' for k in raa_kolonner)
    er_view = con.execute(
        "SELECT count(*) FROM duckdb_views() WHERE view_name = 'enheter'"
    ).fetchone()[0]
    if er_view:
        con.execute("DROP VIEW enheter")
    con.execute("DROP TABLE IF EXISTS enheter_raa")
    con.execute(f"""
        CREATE OR REPLACE TABLE enheter AS
        WITH r AS (SELECT {utvalg} FROM {kilde})
        SELECT *,
            count(*) OVER (PARTITION BY organisasjonsnummer) AS _antall_samme_orgnr,
            count(*) OVER (PARTITION BY upper(trim(navn)), forretningsadresse_postnummer)
                AS _antall_samme_navn_postnr
        FROM r
    """)
    return con.execute("SELECT count(*) FROM enheter").fetchone()[0]


def last_inn_postnummer(con: duckdb.DuckDBPyConnection, fil: Path | str = RAA_POSTNUMMER) -> int:
    """Postens register er tabulatorseparert: postnummer, poststed, kommunenummer,
    kommunenavn, kategori. Filen finnes både som UTF-8 og ANSI (latin-1)."""
    raa = Path(fil).read_bytes()
    try:
        tekst = raa.decode("utf-8")
    except UnicodeDecodeError:
        tekst = raa.decode("latin-1")
    if "\ufffd" in tekst or "ï¿½" in tekst:
        raise ValueError(
            f"{fil} inneholder ødelagte tegn (æ/ø/å er erstattet). "
            "Last ned filen på nytt med 'Lagre link som'."
        )
    rader = []
    for linje in tekst.splitlines():
        felt = linje.split("\t")
        if len(felt) >= 5:
            rader.append(tuple(felt[:5]))
    con.execute("CREATE OR REPLACE TABLE postnummer (postnummer VARCHAR, poststed VARCHAR, "
                "kommunenummer VARCHAR, kommunenavn VARCHAR, kategori VARCHAR)")
    con.executemany("INSERT INTO postnummer VALUES (?, ?, ?, ?, ?)", rader)
    return len(rader)


def kolonner(con: duckdb.DuckDBPyConnection, tabell: str = "enheter") -> set[str]:
    try:
        return {rad[0] for rad in con.execute(f"DESCRIBE {tabell}").fetchall()}
    except duckdb.CatalogException:
        return set()
