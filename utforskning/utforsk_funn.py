from dq import database

con = database.koble_til()

print("\nK02: AS uten næringskode, fordelt på status")
print(con.sql("""
    SELECT coalesce(konkurs, '?') AS konkurs,
           coalesce(under_avvikling, '?') AS under_avvikling,
           year(try_cast(registreringsdatoenhetsregisteret AS DATE)) AS reg_aar,
           count(*) AS antall
    FROM enheter
    WHERE organisasjonsform_kode = 'AS' AND naeringskode1_kode IS NULL
    GROUP BY ALL ORDER BY antall DESC LIMIT 10
"""))

print("\nS01: Stiftet etter registrering, fordelt på organisasjonsform")
print(con.sql("""
    SELECT organisasjonsform_kode,
           count(*) AS antall,
           median(try_cast(stiftelsesdato AS DATE)
                  - try_cast(registreringsdatoenhetsregisteret AS DATE)) AS median_dager
    FROM enheter
    WHERE try_cast(stiftelsesdato AS DATE) > try_cast(registreringsdatoenhetsregisteret AS DATE)
    GROUP BY ALL ORDER BY antall DESC LIMIT 10
"""))

print("\nS04: Poststeder som ikke stemmer med Posten")
print(con.sql("""
    SELECT e.forretningsadresse_poststed AS brreg, p.poststed AS posten, count(*) AS antall
    FROM enheter e JOIN postnummer p ON p.postnummer = e.forretningsadresse_postnummer
    WHERE upper(trim(e.forretningsadresse_poststed)) <> upper(p.poststed)
    GROUP BY ALL ORDER BY antall DESC LIMIT 10
"""))

print("\nU02: Hyppigste navn blant mulige duplikater")
print(con.sql("""
    SELECT organisasjonsform_kode, upper(trim(navn)) AS navn, count(*) AS antall
    FROM enheter WHERE _antall_samme_navn_postnr > 1
    GROUP BY ALL ORDER BY antall DESC LIMIT 10
"""))