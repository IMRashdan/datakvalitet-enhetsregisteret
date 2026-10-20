import argparse
from pathlib import Path

from dq import database, kontroller, profilering, rapport
from dq.last_ned import last_ned_enheter

RESULTATMAPPE = Path("resultater")


def kommando_kolonner() -> None:
    con = database.koble_til()
    database.last_inn_enheter(con)
    for rad in con.execute("SELECT column_name FROM (DESCRIBE enheter)").fetchall():
        if not rad[0].startswith("_"):
            print(rad[0])


def kommando_kontroller() -> None:
    con = database.koble_til()
    print("Laster inn Enhetsregisteret ...", flush=True)
    antall = database.last_inn_enheter(con)
    print(f"Lastet inn {antall:,} enheter".replace(",", " "))

    if database.RAA_POSTNUMMER.exists():
        print(f"Lastet inn {database.last_inn_postnummer(con)} postnummer fra Posten")
    else:
        print(f"Fant ikke {database.RAA_POSTNUMMER} – hopper over kontroller mot Posten")

    print("Kjører kontroller:")
    resultater, hoppet_over = kontroller.kjor_alle(con, vis_fremdrift=True)
    kontroller.lagre_historikk(con, resultater)
    print("Profilerer kolonner ...", flush=True)
    profil = profilering.profiler(con)

    RESULTATMAPPE.mkdir(exist_ok=True)
    rapport.skriv_csv(resultater, RESULTATMAPPE / "kontrollresultater.csv")
    rapport.skriv_markdown(resultater, hoppet_over, profil, antall,
                           RESULTATMAPPE / "kvalitetsrapport.md")

    for r in resultater:
        print(f"  {r.kontroll.id}  {r.kontroll.navn:<42} {r.avvik:>9,} avvik ({r.andel:.3%})"
              .replace(",", " "))
    for k, grunn in hoppet_over:
        print(f"  {k.id}  {k.navn:<42} ikke kjørt: {grunn}")
    print(f"\nRapport skrevet til {RESULTATMAPPE}/kvalitetsrapport.md")


def main() -> None:
    parser = argparse.ArgumentParser(description="Datakvalitetsanalyse av Enhetsregisteret")
    parser.add_argument("kommando", choices=["last-ned", "kolonner", "kontroller", "alt"])
    args = parser.parse_args()

    if args.kommando in ("last-ned", "alt"):
        last_ned_enheter()
    if args.kommando == "kolonner":
        kommando_kolonner()
    if args.kommando in ("kontroller", "alt"):
        kommando_kontroller()


if __name__ == "__main__":
    main()
