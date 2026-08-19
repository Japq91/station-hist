import json

from senamhi_downloader import settings


def load_stations() -> list[dict]:
    with open(settings.STATIONS_FILE_PATH, encoding="utf-8") as f:
        return json.load(f)
