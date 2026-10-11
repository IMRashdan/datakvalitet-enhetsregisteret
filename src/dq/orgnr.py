"""Validering av organisasjonsnummer med modulus 11."""

VEKTER = (3, 2, 7, 6, 5, 4, 3, 2)


def kontrollsiffer(forste_atte: str) -> int | None:
    """Beregner kontrollsifferet for de åtte første sifrene.

    Returnerer None hvis sifrene ikke kan gi et gyldig nummer (rest 10).
    """
    rest = sum(int(s) * v for s, v in zip(forste_atte[:8], VEKTER, strict=True)) % 11
    siffer = 0 if rest == 0 else 11 - rest
    return None if siffer == 10 else siffer


def gyldig_orgnr(orgnr: str | None) -> bool:
    """True hvis orgnr er ni sifre med korrekt kontrollsiffer."""
    if orgnr is None:
        return False
    orgnr = orgnr.strip()
    if len(orgnr) != 9 or not orgnr.isdigit():
        return False
    return kontrollsiffer(orgnr[:8]) == int(orgnr[8])
