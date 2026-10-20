import duckdb


def profiler(con: duckdb.DuckDBPyConnection, tabell: str = "enheter") -> list[dict]:
    totalt = con.execute(f"SELECT count(*) FROM {tabell}").fetchone()[0]
    profil = []
    for (kol,) in con.execute(f"SELECT column_name FROM (DESCRIBE {tabell})").fetchall():
        if kol.startswith("_"):  # hjelpekolonner, ikke en del av registeret
            continue
        manglende, distinkte = con.execute(
            f"SELECT count(*) FILTER (WHERE {kol} IS NULL OR trim({kol}) = ''), "
            f"approx_count_distinct({kol}) FROM {tabell}"
        ).fetchone()
        profil.append({
            "kolonne": kol,
            "manglende": manglende,
            "andel_manglende": manglende / totalt if totalt else 0.0,
            "distinkte": distinkte,
        })
    return sorted(profil, key=lambda p: p["andel_manglende"], reverse=True)
