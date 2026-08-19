"""Descarga datos del portal 'operativo' (mapa-estaciones-2), el mismo que
usa Garua. A diferencia del portal 'climatico', aqui no hay captcha ni
login: solo se necesita un navegador real para pasar el chequeo Cloudflare
Turnstile, y los datos se obtienen interceptando via CDP la respuesta del
endpoint AJAX que se dispara al cambiar el select de periodo (CBOFiltro),
en vez de leerlos de un archivo descargado por el navegador.

Adaptado de garua/scraping/scraper.py (danyneyra/senamhi-scraper).
"""

from __future__ import annotations

import asyncio
import random
from urllib.parse import urlencode

import zendriver as zd
from zendriver import cdp

from senamhi_downloader.browser import get_browser_config
from senamhi_downloader.operativo import settings
from senamhi_downloader.operativo.csv_manager import CSVManager
from senamhi_downloader.operativo.html_utils import extract_select_options


def build_station_url(station: dict) -> str:
    params = {
        "cod": station["codigo"],
        "estado": station["estado"],
        "tipo_esta": station["tipo"],
        "cate": station["categoria"],
        "cod_old": station["codigo_legado"],
    }
    return f"{settings.BASE_URL}?{urlencode(params)}"


def _filter_options_by_period(options: list[dict], start_year: int, end_year: int) -> list[dict]:
    filtered = []
    for option in options:
        value = option["value"].strip()
        if len(value) != 6 or not value.isdigit():
            continue
        year = int(value[:4])
        if start_year <= year <= end_year:
            filtered.append(option)
    return filtered


async def _capture_post_response(page, response_queue: asyncio.Queue, trigger_action) -> str:
    while not response_queue.empty():
        response_queue.get_nowait()

    await trigger_action()

    request_id = await asyncio.wait_for(response_queue.get(), timeout=settings.TIMEOUT_SECONDS)
    body, _ = await page.send(cdp.network.get_response_body(request_id))
    return body


async def _setup_page(browser, url: str):
    page = await browser.get(url)
    await page.send(cdp.network.enable())

    response_queue: asyncio.Queue = asyncio.Queue()
    pending_request_ids: set = set()

    async def on_response_received(event: cdp.network.ResponseReceived):
        if settings.DATA_ENDPOINT in str(event.response.url):
            pending_request_ids.add(event.request_id)

    async def on_loading_finished(event: cdp.network.LoadingFinished):
        if event.request_id in pending_request_ids:
            pending_request_ids.discard(event.request_id)
            await response_queue.put(event.request_id)

    page.add_handler(cdp.network.ResponseReceived, on_response_received)
    page.add_handler(cdp.network.LoadingFinished, on_loading_finished)

    tab_elem = await page.wait_for(selector="a#tabla-tab")
    await tab_elem.click()

    select_found = await page.wait_for(selector="select#CBOFiltro")
    if not select_found:
        raise RuntimeError("Select CBOFiltro no encontrado")

    try:
        await asyncio.wait_for(response_queue.get(), timeout=15)
    except asyncio.TimeoutError:
        pass

    return page, response_queue


async def _process_option(page, response_queue, option, csv_manager: CSVManager) -> bool:
    async def select_action():
        option_elem = await page.query_selector(f"option[value='{option['value']}']")
        if not option_elem:
            raise RuntimeError(f"Opcion no encontrada en el select: {option['value']}")
        await option_elem.select_option()

    for attempt in range(1, settings.MAX_RETRIES + 2):
        try:
            full_html = await _capture_post_response(page, response_queue, select_action)
            rows = csv_manager.add_table_data(full_html, option["value"])
            print(f"    {option['text']}: {rows} filas")
            return True
        except Exception as e:
            if attempt <= settings.MAX_RETRIES:
                print(f"    [!] Reintento {attempt} para {option['value']}: {e}")
                await asyncio.sleep(settings.RETRY_SLEEP)
            else:
                print(f"    [!] Fallo definitivo en {option['value']}: {e}")
    return False


async def download_station(browser, station: dict, start_year: int, end_year: int) -> str | None:
    url = build_station_url(station)
    print(f"  Abriendo: {url}")

    page, response_queue = await _setup_page(browser, url)

    select_html = await (await page.wait_for(selector="select#CBOFiltro")).get_html()
    options = extract_select_options(select_html)
    period_options = _filter_options_by_period(options, start_year, end_year)

    if not period_options:
        print(f"  [!] Sin datos disponibles entre {start_year} y {end_year}")
        return None

    print(f"  {len(period_options)} periodo(s) a descargar")
    csv_manager = CSVManager(station)

    prev_year = None
    ok_count = 0
    for i, option in enumerate(period_options, 1):
        current_year = option["value"][:4]
        if prev_year is not None and current_year != prev_year:
            await asyncio.sleep(settings.YEAR_BOUNDARY_SLEEP)
        prev_year = current_year

        if await _process_option(page, response_queue, option, csv_manager):
            ok_count += 1

        if i < len(period_options):
            await asyncio.sleep(random.uniform(settings.JITTER_MIN, settings.JITTER_MAX))

    if ok_count == 0:
        print("  [!] No se pudo descargar ningun periodo")
        return None

    filepath = csv_manager.save(start_year, end_year)
    print(f"  OK -> {filepath} ({ok_count}/{len(period_options)} periodos)")
    return filepath


async def download_all(stations: list[dict], start_year: int, end_year: int) -> None:
    if not stations:
        return

    settings.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    browser = await zd.start(config=get_browser_config())
    try:
        for i, station in enumerate(stations, 1):
            print(f"\n[{i}/{len(stations)}] Estacion: {station['nombre']} ({station['codigo']}) - {station['departamento']}")
            try:
                await download_station(browser, station, start_year, end_year)
            except Exception as e:
                print(f"  [!] Error con la estacion {station['codigo']}: {e}")
    finally:
        await browser.stop()

    print(f"\nListo. Revisa los CSV en {settings.DOWNLOAD_DIR}")
