from pathlib import Path

import pytest

from dq import database, kontroller
from dq.database import normaliser_kolonnenavn

FIXTURES = Path(__file__).parent / "fixtures"

FORVENTET_AVVIK = {
    "G01": 1, "G02": 1, "G03": 1, "G04": 1,
    "K01": 1, "K02": 1,
    "U01": 2, "U02": 2,
    "S01": 1, "S02": 1, "S03": 1, "S04": 1,
}


@pytest.fixture
def con():
    con = database.koble_til(":memory:")
    database.last_inn_enheter(con, FIXTURES / "enheter_utvalg.csv")
    database.last_inn_postnummer(con, FIXTURES / "postnummer_utvalg.txt")
    return con


def test_alle_kontroller_finner_forventet_antall_avvik(con):
    resultater, hoppet_over = kontroller.kjor_alle(con)
    assert hoppet_over == []
    faktisk = {r.kontroll.id: r.avvik for r in resultater}
    assert faktisk == FORVENTET_AVVIK


def test_kontroll_hoppes_over_uten_postnummerregister():
    con = database.koble_til(":memory:")
    database.last_inn_enheter(con, FIXTURES / "enheter_utvalg.csv")
    _, hoppet_over = kontroller.kjor_alle(con)
    assert {k.id for k, _ in hoppet_over} == {"S03", "S04"}


def test_postnummerregister_leses_som_latin1(con):
    sql = "SELECT poststed FROM postnummer WHERE postnummer = '9990'"
    poststed = con.execute(sql).fetchone()[0]
    assert poststed == "BÅTSFJORD"


def test_unike_kontroll_id():
    ids = [k.id for k in kontroller.KONTROLLER]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("inn, ut", [
    ("forretningsadresse.postnummer", "forretningsadresse_postnummer"),
    ("antallAnsatte", "antall_ansatte"),
    ("registreringsdatoEnhetsregisteret", "registreringsdato_enhetsregisteret"),
    ("naeringskode1.kode", "naeringskode1_kode"),
])
def test_normaliser_kolonnenavn(inn, ut):
    assert normaliser_kolonnenavn(inn) == ut
