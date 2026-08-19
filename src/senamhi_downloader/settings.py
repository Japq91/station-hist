import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIONS_FILE_PATH = PROJECT_ROOT / "data" / "estaciones.json"
DOWNLOAD_DIR = PROJECT_ROOT / "downloads"

BASE_URL = "https://www.senamhi.gob.pe/site/descarga-datos/"
# La pagina descarga/?cod=X esta pensada para cargarse dentro del flujo
# normal (mapa filtrado por departamento -> clic en el globo -> pestana
# Descarga), no como link directo. Navegamos al mapa filtrado y dejamos que
# el usuario haga clic en el globo correcto, igual que en el uso manual.
MAP_URL_TEMPLATE = "https://www.senamhi.gob.pe/site/descarga-datos/map_hist_data.php?dp={dep_slug}"

SENAMHI_EMAIL = os.getenv("SENAMHI_EMAIL", "")
SENAMHI_PASSWORD = os.getenv("SENAMHI_PASSWORD", "")
GARUA_BROWSER_PATH = os.getenv("GARUA_BROWSER_PATH", "")

TIMEOUT_SECONDS = 60
