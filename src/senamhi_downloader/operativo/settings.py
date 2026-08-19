"""Configuracion del tool 'operativo' (mapa-estaciones-2, el mismo que usa
Garua). A diferencia del portal 'climatico' (site/descarga-datos), este no
pide captcha ni login: solo hace falta un navegador real para pasar el
chequeo Cloudflare Turnstile.
"""

from pathlib import Path

from senamhi_downloader.settings import PROJECT_ROOT

STATIONS_FILE_PATH = PROJECT_ROOT / "data_operativo" / "estaciones.json"
DOWNLOAD_DIR = PROJECT_ROOT / "downloads_operativo"

BASE_URL = "https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/map_red_graf.php"
# Identificador interno del endpoint AJAX que responde con la tabla de datos
# al cambiar el select de periodo (CBOFiltro). Definido por SENAMHI, no por
# nosotros; visto interceptando la respuesta de red al usar el sitio.
DATA_ENDPOINT = "__dt_est_tp_0s3n"

CSV_SEPARATOR = ";"
CSV_ENCODING = "utf-8"

# Rango de anios por defecto si no se especifica --yeari/--yearf
YEAR_DEFAULT_START = 2017
YEAR_DEFAULT_END = 2026

TIMEOUT_SECONDS = 30
MAX_RETRIES = 2
RETRY_SLEEP = 5.0
JITTER_MIN = 0.3
JITTER_MAX = 0.9
YEAR_BOUNDARY_SLEEP = 1.5
