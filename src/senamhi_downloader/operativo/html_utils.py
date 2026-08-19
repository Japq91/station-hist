"""Parseo de HTML de SENAMHI (select de periodos y tabla de datos). Portado
de Garua (garua/utils/html_utils.py), sin la parte de extraccion de
metadata de estacion (ya la tenemos guardada en data_operativo/estaciones.json).
"""

import re

from bs4 import BeautifulSoup

from senamhi_downloader.operativo import settings

HTML_PARSER = "html.parser"


def extract_select_options(html_content: str, select_id: str = "CBOFiltro") -> list[dict]:
    soup = BeautifulSoup(html_content, HTML_PARSER)
    select_element = soup.find("select", id=select_id)
    if not select_element:
        raise ValueError(f"No se encontro ningun select con ID '{select_id}'")

    return [
        {
            "value": option.get("value", ""),
            "text": option.get_text(strip=True),
            "selected": option.has_attr("selected"),
            "disabled": option.has_attr("disabled"),
        }
        for option in select_element.find_all("option")
    ]


def _date_format(date_str: str) -> tuple[int, int, int] | None:
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str) or re.match(r"^\d{4}/\d{2}/\d{2}$", date_str):
        year, month, day = date_str.split("-") if "-" in date_str else date_str.split("/")
        if 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
            return int(year), int(month), int(day)
    elif re.match(r"^\d{2}/\d{2}/\d{4}$", date_str) or re.match(r"^\d{2}-\d{2}-\d{4}$", date_str):
        day, month, year = date_str.split("/" if "/" in date_str else "-")
        if 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
            return int(year), int(month), int(day)
    return None


def _process_table_row(row, row_index: int, separator: str) -> list[str] | None:
    cells = row.find_all(["td", "th"])
    row_data = []

    for cell_idx, cell in enumerate(cells):
        cell_text = cell.get_text(strip=True)

        if "Fatal error" in cell_text or "Warning" in cell_text or "thrown in" in cell_text:
            print(f"  [!] Fila {row_index + 1} contiene error PHP del servidor, se descarta.")
            return None

        cell_text = re.sub(r"\s+", " ", cell_text)
        if separator in cell_text:
            cell_text = f'"{cell_text}"'

        if row_index > 0 and cell_idx == 0:
            date_format = _date_format(cell_text)
            if date_format is None:
                print(f"  [!] La primera celda de la fila {row_index + 1} no es una fecha valida: '{cell_text}'")
                return None
            year, month, day = date_format
            row_data.extend([f"{year:04d}", f"{month:02d}", f"{day:02d}"])
        else:
            if cell_text.strip() in ("S/D", ""):
                cell_text = "S/D"
            elif cell_text.strip() == "T":
                cell_text = "T"
            row_data.append(cell_text)

    return row_data if row_data and any(cell.strip() for cell in row_data) else None


def html_table_to_csv(html_content: str, separator: str = settings.CSV_SEPARATOR, start_line: int = 0) -> str:
    soup = BeautifulSoup(html_content, HTML_PARSER)
    table = soup.find("table")
    if not table:
        return ""

    csv_lines = []
    seen_rows = set()
    rows = table.find_all("tr")

    for row_index, row in enumerate(rows):
        if start_line and row_index < start_line:
            continue
        row_data = _process_table_row(row, row_index, separator)
        if not row_data:
            continue

        row_content = separator.join(row_data)
        if row_index > 0:
            if row_content in seen_rows:
                print(f"  [!] Fila duplicada detectada en linea {row_index + 1}, se omite.")
                continue
            seen_rows.add(row_content)

        csv_lines.append(row_content)

    return "\n".join(csv_lines)
