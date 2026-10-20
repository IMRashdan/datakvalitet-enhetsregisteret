import csv
from datetime import date
from pathlib import Path

from dq.kontroller import Kontroll, Resultat


def skriv_csv(resultater: list[Resultat], fil: Path) -> None:
    with open(fil, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "kontroll_id", "navn", "dimensjon", "kontrollert", "avvik", "andel", "eksempler"
        ])
        for r in resultater:
            k = r.kontroll
            w.writerow([k.id, k.navn, k.dimensjon, r.kontrollert, r.avvik,
                        f"{r.andel:.6f}", " ".join(r.eksempler)])


def skriv_markdown(resultater: list[Resultat], hoppet_over: list[tuple[Kontroll, str]],
                   profil: list[dict], antall_enheter: int, fil: Path) -> None:
    linjer = [
        "# Kvalitetsrapport – Enhetsregisteret",
        "",
        f"Generert {date.today():%d.%m.%Y} · {antall_enheter:,} enheter".replace(",", " "),
        "",
        "## Kontroller",
        "",
        "| ID | Kontroll | Dimensjon | Kontrollert | Avvik | Andel |",
        "|---|---|---|---:|---:|---:|",
    ]
    for r in sorted(resultater, key=lambda r: (r.kontroll.dimensjon, r.kontroll.id)):
        k = r.kontroll
        linjer.append(f"| {k.id} | {k.navn} | {k.dimensjon} | {r.kontrollert:,} | "
                      f"{r.avvik:,} | {r.andel:.3%} |".replace(",", " "))
    if hoppet_over:
        linjer += ["", "**Ikke kjørt:**", ""]
        linjer += [f"- {k.id} {k.navn} ({grunn})" for k, grunn in hoppet_over]
    linjer += ["", "## Kompletthet per kolonne (10 med flest manglende verdier)", "",
               "| Kolonne | Manglende | Andel | Distinkte (ca.) |", "|---|---:|---:|---:|"]
    for p in profil[:10]:
        linjer.append(f"| `{p['kolonne']}` | {p['manglende']:,} | {p['andel_manglende']:.1%} | "
                      f"{p['distinkte']:,} |".replace(",", " "))
    fil.write_text("\n".join(linjer) + "\n", encoding="utf-8")
