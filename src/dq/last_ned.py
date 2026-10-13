import shutil
import urllib.request
from pathlib import Path

from dq.database import RAA_ENHETER

URL_ENHETER = "https://data.brreg.no/enhetsregisteret/api/enheter/lastned/csv"


def last_ned_enheter(mal: Path = RAA_ENHETER) -> Path:
    mal.parent.mkdir(parents=True, exist_ok=True)
    print(f"Laster ned {URL_ENHETER} ...")
    with urllib.request.urlopen(URL_ENHETER) as svar, open(mal, "wb") as f:
        shutil.copyfileobj(svar, f)
    print(f"Lagret {mal} ({mal.stat().st_size / 1e6:.1f} MB)")
    return mal
