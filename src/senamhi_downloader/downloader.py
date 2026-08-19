"""Orquesta la descarga de datos historicos de SENAMHI (site/descarga-datos)
para una lista de estaciones.

Automatiza lo repetitivo (abrir el navegador, navegar a cada estacion,
detectar y mover el archivo descargado). Los pasos de verificacion
(captcha de imagen y aceptar terminos y condiciones) se resuelven a mano
en la ventana del navegador que se abre — no se intenta evadir ni
resolver el captcha por script.
"""

from __future__ import annotations

import asyncio
import shutil
import time
from pathlib import Path

import zendriver as zd

from senamhi_downloader import settings
from senamhi_downloader.browser import get_browser_config
from senamhi_downloader.stations import department_slug


def _newest_file_since(folder: Path, since_ts: float) -> Path | None:
    candidates = [
        p for p in folder.glob("*")
        if p.is_file() and p.stat().st_mtime >= since_ts
        and not p.name.endswith((".crdownload", ".tmp", ".part"))
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _wait_for_new_file(folder: Path, since_ts: float, timeout: int = 120) -> Path | None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        found = _newest_file_since(folder, since_ts)
        if found:
            # asegura que el archivo terminó de escribirse (tamaño estable)
            size_a = found.stat().st_size
            time.sleep(1)
            if found.exists() and found.stat().st_size == size_a:
                return found
        time.sleep(1)
    return None


async def download_all(stations: list[dict]) -> None:
    settings.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    browser = await zd.start(config=get_browser_config())
    try:
        print(f"\nAbriendo {settings.BASE_URL} para iniciar sesion...")
        await browser.get(settings.BASE_URL)
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
            start_ts = time.time()

            await browser.get(url)

            print(
                f"  -> En la ventana del navegador: busca el globo de '{name}' "
                "(o su codigo), haz clic en el, ve a la pestana 'Descarga', "
                "resuelve el/los captcha, acepta terminos y condiciones, "
                "y haz clic en 'Descargar'."
            )

            while True:
                print("  [1] Aun no he terminado (esperar)")
                print("  [2] Ya descargue -> mover archivo y continuar")
                print("  [3] Saltar esta estacion")
                choice = input("  Elige una opcion [1/2/3]: ").strip()

                if choice == "2":
                    found = _wait_for_new_file(settings.BROWSER_DOWNLOADS_DIR, start_ts, timeout=30)
                    if not found:
                        print(
                            f"  [!] No se detecto un archivo nuevo en {settings.BROWSER_DOWNLOADS_DIR}. "
                            "Espera a que termine la descarga o revisa la carpeta configurada."
                        )
                        continue
                    dest = settings.DOWNLOAD_DIR / found.name
                    shutil.move(str(found), str(dest))
                    print(f"  OK -> guardado en {dest}")
                    break
                elif choice == "3":
                    print("  Saltando estacion...")
                    break
                # choice == "1" (o cualquier otra cosa): vuelve a mostrar el menu

    finally:
        await browser.stop()
