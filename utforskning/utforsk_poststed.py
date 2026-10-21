from dq import database

con = database.koble_til()
print(con.sql("""
    SELECT e.forretningsadresse_poststed AS brreg,
           p.poststed AS posten,
           count(*) AS antall
    FROM enheter e
    JOIN postnummer p ON p.postnummer = e.forretningsadresse_postnummer
    WHERE upper(trim(e.forretningsadresse_poststed)) <> upper(p.poststed)
    GROUP BY ALL
    ORDER BY antall DESC
    LIMIT 15
"""))