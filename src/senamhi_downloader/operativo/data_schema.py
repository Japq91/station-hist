"""Headers CSV por tipo/estado de estacion. Portado de Garua
(garua/models/data_schema.py), adaptado a los strings crudos de SENAMHI
('M'/'H', 'REAL'/'DIFERIDO'/'AUTOMATICA') en vez de enums pydantic.

Las listas fijas suponen que la estacion tiene todos los sensores. Algunas
automaticas no los tienen (ej: Ceres 112278, sin humedad) y su tabla trae
una columna menos; por eso, para las meteorologicas automaticas, el
encabezado se arma desde la propia tabla con headers_from_table().
"""

import unicodedata

METEOROLOGICAL_CONVENTIONAL_HEADERS = [
    "Año", "Mes", "Día",
    "Temp. Máx (°C)", "Temp. Mín (°C)", "Humedad (%)", "Precipitación (mm)",
]

METEOROLOGICAL_AUTOMATIC_HEADERS = [
    "Año", "Mes", "Día", "Hora",
    "Temperatura (°C)", "Precipitación (mm)", "Humedad (%)",
    "Dir. Viento (°)", "Vel. Viento (m/s)",
]

HYDROLOGICAL_CONVENTIONAL_HEADERS = [
    "Año", "Mes", "Día",
    "Nivel del río (m) 06", "Nivel del río (m) 10",
    "Nivel del río (m) 14", "Nivel del río (m) 18",
]

HYDROLOGICAL_AUTOMATIC_HEADERS = [
    "Año", "Mes", "Día", "Hora",
    "Nivel del río (m)", "Precipitación (mm/hora)",
]


def get_headers_for_station(station: dict) -> list[str]:
    tipo = station["tipo"]
    estado = station["estado"]

    if tipo == "M":
        if estado == "AUTOMATICA":
            return METEOROLOGICAL_AUTOMATIC_HEADERS.copy()
        return METEOROLOGICAL_CONVENTIONAL_HEADERS.copy()
    elif tipo == "H":
        if estado == "AUTOMATICA":
            return HYDROLOGICAL_AUTOMATIC_HEADERS.copy()
        return HYDROLOGICAL_CONVENTIONAL_HEADERS.copy()

    raise ValueError(f"Tipo de estacion desconocido: {tipo}")


# Raiz (minusculas, sin tildes) que identifica cada columna en el encabezado
# de la tabla HTML; sirve tanto para "Direccion del viento" como para
# "Dir. Viento". "hora" va al final porque tambien aparece en
# "precipitacion (mm/hora)".
_AUTOMATIC_KEYWORDS = [
    ("temp", "Temperatura (°C)"),
    ("precip", "Precipitación (mm)"),
    ("hum", "Humedad (%)"),
    ("dir", "Dir. Viento (°)"),
    ("vel", "Vel. Viento (m/s)"),
    ("hora", "Hora"),
]


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def headers_from_table(station: dict, header_cells: list[str]) -> list[str] | None:
    """Encabezado CSV segun las columnas que de verdad trae la tabla HTML.

    La primera celda es la fecha (se escribe como Año;Mes;Día). Devuelve None
    si la estacion no es meteorologica automatica o si alguna columna no se
    reconoce; en ese caso se usa la lista fija de get_headers_for_station().
    """
    if station["tipo"] != "M" or station["estado"] != "AUTOMATICA" or len(header_cells) < 2:
        return None

    headers = ["Año", "Mes", "Día"]
    for cell in header_cells[1:]:
        name = _normalize(cell)
        match = next((h for key, h in _AUTOMATIC_KEYWORDS if key in name), None)
        if match is None or match in headers:
            return None
        headers.append(match)
    return headers


def get_start_line(station: dict) -> int:
    """Fila desde la que empezar a leer la tabla HTML (salta encabezados extra)."""
    return 1 if station["estado"] == "AUTOMATICA" else 2
