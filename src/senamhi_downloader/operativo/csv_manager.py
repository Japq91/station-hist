"""Acumula las filas de cada periodo consultado y las guarda en un unico
CSV consolidado por estacion, nombrado por el CODIGO de SENAMHI (no por el
nombre de la estacion).
"""

from senamhi_downloader.operativo import settings
from senamhi_downloader.operativo.data_schema import get_headers_for_station
from senamhi_downloader.operativo.html_utils import html_table_to_csv


class CSVManager:
    def __init__(self, station: dict):
        self.station = station
        self.headers = get_headers_for_station(station)
        self.start_line = 1 if station["estado"] == "AUTOMATICA" else 2
        self.buffer: list[str] = [settings.CSV_SEPARATOR.join(self.headers)]

    def add_table_data(self, table_html: str, option_value: str) -> int:
        csv_content = html_table_to_csv(
            table_html, separator=settings.CSV_SEPARATOR, start_line=self.start_line
        )
        if not csv_content:
            return 0
        lines = [line for line in csv_content.split("\n") if line.strip()]
        self.buffer.extend(lines)
        return len(lines)

    def save(self, start_year: int, end_year: int) -> str:
        settings.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{self.station['codigo']}-{start_year:04d}-{end_year:04d}.csv"
        filepath = settings.DOWNLOAD_DIR / filename
        filepath.write_text("\n".join(self.buffer), encoding=settings.CSV_ENCODING)
        return str(filepath)
