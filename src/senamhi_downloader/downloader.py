"""Orquesta la descarga de datos historicos de SENAMHI (site/descarga-datos)
para una lista de estaciones.

Automatiza lo repetitivo (abrir el navegador, navegar al mapa filtrado por
departamento de cada estacion). Los pasos de verificacion (captcha de
imagen y aceptar terminos y condiciones) y el clic en el globo de la
estacion se resuelven a mano en la ventana del navegador que se abre — no
se intenta evadir ni resolver el captcha por script.

Chrome bloquea las descargas automaticas cuando esta controlado via CDP
(protocolo de depuracion remota, que es como zendriver lo maneja) a menos
que se llame explicitamente a Browser.setDownloadBehavior. Por eso se usa
page.set_download_path() en cada pestana para que los archivos se guarden
directo en DOWNLOAD_DIR, sin pasar por la carpeta de Descargas del SO.
"""

from __future__ import annotations

import zendriver as zd

from senamhi_downloader import settings
from senamhi_downloader.browser import get_browser_config
from senamhi_downloader.stations import department_slug


async def download_all(stations: list[dict]) -> None:
    if not stations:
        return

    settings.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Los archivos se guardaran directamente en: {settings.DOWNLOAD_DIR}")

    browser = await zd.start(config=get_browser_config())
    try:
        first_dep_slug = department_slug(stations[0]["departamento"])
        first_url = settings.MAP_URL_TEMPLATE.format(dep_slug=first_dep_slug)

        print(f"\nAbriendo {first_url} para iniciar sesion...")
        page = await browser.get(first_url)
        await page.set_download_path(settings.DOWNLOAD_DIR)
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

            page = await browser.get(url)
            await page.set_download_path(settings.DOWNLOAD_DIR)

            print(
                f"  -> En la ventana del navegador: busca el globo de '{name}' "
                "(o su codigo), haz clic en el, ve a la pestana 'Descarga', "
                "resuelve el/los captcha, acepta terminos y condiciones, "
                "y haz clic en 'Descargar' (se guardara directo en "
                f"{settings.DOWNLOAD_DIR})."
            )
            input("  Presiona ENTER aqui para pasar a la siguiente estacion... ")

    finally:
        await browser.stop()

    print(f"\nListo. Revisa los archivos descargados en {settings.DOWNLOAD_DIR}")
