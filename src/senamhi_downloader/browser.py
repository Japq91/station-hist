"""Deteccion de navegadores Chromium compatibles con zendriver.

Adaptado de la logica de Garua (danyneyra/senamhi-scraper), que ya funciona
sin configuracion adicional detectando Chrome/Brave/Edge automaticamente
via zendriver.Config().
"""

from __future__ import annotations

import os
import sys
import shutil
from dataclasses import dataclass
from pathlib import Path

from zendriver import Config

from senamhi_downloader import settings
from senamhi_downloader.exceptions import BrowserNotFoundError

ENV_BROWSER_PATH = "GARUA_BROWSER_PATH"


@dataclass(frozen=True)
class BrowserCheck:
    ok: bool
    path: str | None
    source: str | None
    message: str


def _is_executable(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


def _path_from_env() -> BrowserCheck | None:
    if not settings.GARUA_BROWSER_PATH:
        return None

    browser_path = Path(settings.GARUA_BROWSER_PATH).expanduser()
    if _is_executable(browser_path):
        return BrowserCheck(True, str(browser_path), ENV_BROWSER_PATH, "Navegador configurado por variable de entorno.")

    return BrowserCheck(False, str(browser_path), ENV_BROWSER_PATH, f"{ENV_BROWSER_PATH} apunta a una ruta invalida: {browser_path}")


def _path_from_zendriver() -> BrowserCheck | None:
    try:
        browser_path = Config().browser_executable_path
    except FileNotFoundError:
        return None

    if browser_path:
        return BrowserCheck(True, str(browser_path), "zendriver", "Navegador detectado automaticamente por zendriver.")
    return None


def _edge_candidates() -> list[str]:
    candidates: list[str] = []
    match = shutil.which("msedge") or shutil.which("microsoft-edge")
    if match:
        candidates.append(match)

    if sys.platform == "darwin":
        candidates.append("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge")
    elif sys.platform != "win32":
        for name in ("microsoft-edge", "microsoft-edge-stable"):
            match = shutil.which(name)
            if match:
                candidates.append(match)

    return candidates


def _path_from_edge() -> BrowserCheck | None:
    for candidate in _edge_candidates():
        browser_path = Path(candidate)
        if _is_executable(browser_path):
            return BrowserCheck(True, str(browser_path), "edge", "Microsoft Edge detectado.")
    return None


def check_browser() -> BrowserCheck:
    for finder in (_path_from_env, _path_from_zendriver, _path_from_edge):
        result = finder()
        if result:
            return result

    return BrowserCheck(
        ok=False,
        path=None,
        source=None,
        message=(
            "No se encontro Google Chrome, Brave ni Microsoft Edge. "
            f"Instala uno o define {ENV_BROWSER_PATH} en .env con la ruta del ejecutable."
        ),
    )


def get_browser_config() -> Config:
    browser_check = check_browser()
    if not browser_check.ok or not browser_check.path:
        raise BrowserNotFoundError(browser_check.message)

    return Config(
        browser_executable_path=browser_check.path,
        headless=False,
    )
