import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIONS_FILE_PATH = PROJECT_ROOT / "data" / "estaciones_moquegua.json"
DOWNLOAD_DIR = PROJECT_ROOT / "downloads"

# Carpeta real donde el navegador guarda las descargas (la de tu SO).
# El script mueve el archivo desde aqui hacia DOWNLOAD_DIR una vez que
# confirmas que la descarga terminó.
BROWSER_DOWNLOADS_DIR = Path(os.getenv("BROWSER_DOWNLOADS_DIR", str(Path.home() / "Downloads")))

BASE_URL = "https://www.senamhi.gob.pe/site/descarga-datos/"
DOWNLOAD_URL_TEMPLATE = "https://www.senamhi.gob.pe/site/descarga-datos/descarga/?cod={codigo}"

SENAMHI_EMAIL = os.getenv("SENAMHI_EMAIL", "")
SENAMHI_PASSWORD = os.getenv("SENAMHI_PASSWORD", "")
GARUA_BROWSER_PATH = os.getenv("GARUA_BROWSER_PATH", "")

TIMEOUT_SECONDS = 60
