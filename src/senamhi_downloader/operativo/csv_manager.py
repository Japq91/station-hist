"""Acumula las filas de cada periodo consultado y las guarda en un unico
CSV consolidado por estacion, nombrado por el CODIGO de SENAMHI (no por el
nombre de la estacion).
"""

from senamhi_downloader.operativo import settings
from senamhi_downloader.operativo.data_schema import get_headers_for_station, headers_from_table
from senamhi_downloader.operativo.html_utils import html_table_to_csv, table_header_cells


class CSVManager:
    def __init__(self, station: dict):
        self.station = station
        self.headers = get_headers_for_station(station)
        self.start_line = 1 if station["estado"] == "AUTOMATICA" else 2
        self.headers_checked = False
        self.buffer: list[str] = [settings.CSV_SEPARATOR.join(self.headers)]

    def _update_headers(self, table_html: str) -> None:
        """Ajusta el encabezado a las columnas de la primera tabla recibida."""
        self.headers_checked = True
        headers = headers_from_table(self.station, table_header_cells(table_html))
        if headers and headers != self.headers:
            missing = [h for h in self.headers if h not in headers]
            print(f"    Columnas ausentes en esta estacion: {', '.join(missing)}")
            self.headers = headers
            self.buffer[0] = settings.CSV_SEPARATOR.join(headers)

    def add_table_data(self, table_html: str, option_value: str) -> int:
        if not self.headers_checked:
            self._update_headers(table_html)
        csv_content = html_table_to_csv(
            table_html, separator=settings.CSV_SEPARATOR, start_line=self.start_line
        )
        if not csv_content:
            return 0
        lines = [line for line in csv_content.split("\n") if line.strip()]
        self.buffer.extend(lines)
        return len(lines)

    def save(self, start_year: int, end_year: int) -> str:
        n_cols = len(self.headers)
        bad = sum(1 for line in self.buffer[1:] if len(line.split(settings.CSV_SEPARATOR)) != n_cols)
        if bad:
            print(
                f"  [!] {bad} fila(s) no tienen {n_cols} valores como el encabezado: "
                "revisa el CSV, las columnas pueden estar corridas."
            )
        settings.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{self.station['codigo']}-{start_year:04d}-{end_year:04d}.csv"
        filepath = settings.DOWNLOAD_DIR / filename
        filepath.write_text("\n".join(self.buffer), encoding=settings.CSV_ENCODING)
        return str(filepath)
