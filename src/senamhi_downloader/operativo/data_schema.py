"""Headers CSV por tipo/estado de estacion. Portado de Garua
(garua/models/data_schema.py), adaptado a los strings crudos de SENAMHI
('M'/'H', 'REAL'/'DIFERIDO'/'AUTOMATICA') en vez de enums pydantic.
"""

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


def get_start_line(station: dict) -> int:
    """Fila desde la que empezar a leer la tabla HTML (salta encabezados extra)."""
    return 1 if station["estado"] == "AUTOMATICA" else 2
