"""Orquesta la descarga de datos historicos de SENAMHI (site/descarga-datos)
para una lista de estaciones.

Automatiza lo repetitivo (abrir el navegador, navegar al mapa filtrado por
departamento de cada estacion). Los pasos de verificacion (captcha de
imagen y aceptar terminos y condiciones) y el clic en el globo de la
estacion se resuelven a mano en la ventana del navegador que se abre — no
se intenta evadir ni resolver el captcha por script.

Los archivos descargados se mueven en un solo lote al finalizar todas las
estaciones y cerrar el navegador (no estacion por estacion), buscando por
la nomenclatura q*.txt que usa SENAMHI en la carpeta de Descargas del
sistema.
"""

from __future__ import annotations

import shutil
import time

import zendriver as zd

from senamhi_downloader import settings
from senamhi_downloader.browser import get_browser_config
from senamhi_downloader.stations import department_slug


def _move_downloaded_files(since_ts: float) -> None:
    settings.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    candidates = sorted(
        p for p in settings.BROWSER_DOWNLOADS_DIR.glob("q*.txt")
        if p.is_file() and p.stat().st_mtime >= since_ts
    )
    if not candidates:
        print(
            f"\nNo se encontraron archivos 'q*.txt' nuevos en "
            f"{settings.BROWSER_DOWNLOADS_DIR}"
        )
        return

    print(f"\nMoviendo {len(candidates)} archivo(s) a {settings.DOWNLOAD_DIR}...")
    for f in candidates:
        dest = settings.DOWNLOAD_DIR / f.name
        shutil.move(str(f), str(dest))
        print(f"  {f.name} -> {dest}")


async def download_all(stations: list[dict]) -> None:
    if not stations:
        return

    session_start_ts = time.time()
    browser = await zd.start(config=get_browser_config())
    try:
        first_dep_slug = department_slug(stations[0]["departamento"])
        first_url = settings.MAP_URL_TEMPLATE.format(dep_slug=first_dep_slug)

        print(f"\nAbriendo {first_url} para iniciar sesion...")
        await browser.get(first_url)
        print(
            "  -> En la ventana del navegador: completa el 'Ingreso' "
            "(acepta terminos y condiciones y resuelve el captcha)."
        )
        input("  Presiona ENTER aqui cuando hayas iniciado sesion... ")

        for i, station in enumerate(stations, 1):
            codigo = station["codigo"]
            name = station["name"]
            dep_slug = department_slug(station["departamento"])
            url = settings.MAP_URL_TEMPLATE.format(dep_slug=dep_slug)

            print(f"\n[{i}/{len(stations)}] Estacion: {name} ({codigo}) - {station['departamento']}")
            print(f"  Abriendo mapa filtrado: {url}")

            await browser.get(url)

            print(
                f"  -> En la ventana del navegador: busca el globo de '{name}' "
                "(o su codigo), haz clic en el, ve a la pestana 'Descarga', "
                "resuelve el/los captcha, acepta terminos y condiciones, "
                "y haz clic en 'Descargar'."
            )
            input("  Presiona ENTER aqui para pasar a la siguiente estacion... ")

    finally:
        await browser.stop()

    _move_downloaded_files(session_start_ts)
