import pytest

from dq.orgnr import gyldig_orgnr


@pytest.mark.parametrize("orgnr", ["910000012", "910000020", "974761076"])
def test_gyldige(orgnr):
    assert gyldig_orgnr(orgnr)


@pytest.mark.parametrize("orgnr", [
    "910000013",   # feil kontrollsiffer
    "91000001",    # for kort
    "9100000120",  # for langt
    "91000001A",   # ikke-siffer
    "",
    None,
])
def test_ugyldige(orgnr):
    assert not gyldig_orgnr(orgnr)


def test_sql_makro_gir_samme_svar_som_python():
    """mod11-kontrollen finnes både i Python og som SQL-makro. De skal alltid være enige."""
    import random

    from dq.database import koble_til

    random.seed(1)
    kandidater = [f"{random.randint(0, 999_999_999):09d}" for _ in range(5000)]
    kandidater += ["974761076", "91000001", "91000001A", "", " 910000012 "]
    con = koble_til(":memory:")
    sql_svar = [r[0] for r in con.execute(
        "SELECT gyldig_orgnr(o) FROM unnest(?::VARCHAR[]) AS t(o)", [kandidater]
    ).fetchall()]
    assert sql_svar == [gyldig_orgnr(o) for o in kandidater]
    assert sum(sql_svar) > 0
