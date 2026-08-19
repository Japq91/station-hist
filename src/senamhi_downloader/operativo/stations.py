import json

from senamhi_downloader.operativo import settings


def load_stations() -> list[dict]:
    with open(settings.STATIONS_FILE_PATH, encoding="utf-8") as f:
        return json.load(f)


def find_by_code(codigo: str) -> dict | None:
    codigo = codigo.strip().upper()
    for station in load_stations():
        if codigo in (station["codigo"], station["codigo_legado"], station["codigo_frontend"]):
            return station
    return None


def search_by_name(query: str) -> list[dict]:
    query_upper = query.strip().upper()
    if not query_upper:
        return []
    stations = load_stations()
    starts_with = [s for s in stations if s["nombre"].upper().startswith(query_upper)]
    contains = [
        s for s in stations
        if query_upper in s["nombre"].upper() and s not in starts_with
    ]
    return starts_with + contains


def filter_by_department(departamento: str) -> list[dict]:
    dep_upper = departamento.strip().upper()
    return [s for s in load_stations() if s["departamento"].upper() == dep_upper]


def list_departments() -> list[str]:
    return sorted({s["departamento"] for s in load_stations() if s["departamento"]})


def filter_by_bbox(lat1: float, lat2: float, lon1: float, lon2: float) -> list[dict]:
    """Estaciones dentro del rectangulo definido por dos esquinas (orden libre)."""
    lat_min, lat_max = sorted((lat1, lat2))
    lon_min, lon_max = sorted((lon1, lon2))
    return [
        s for s in load_stations()
        if s["lat"] is not None and s["lon"] is not None
        and lat_min <= s["lat"] <= lat_max and lon_min <= s["lon"] <= lon_max
    ]
