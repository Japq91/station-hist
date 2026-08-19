class BrowserNotFoundError(Exception):
    """No se encontró un navegador Chromium compatible."""


class CaptchaTimeoutError(Exception):
    """El usuario no resolvió el captcha/T&C dentro del tiempo esperado."""


class DownloadFailedError(Exception):
    """El archivo esperado no apareció en la carpeta de descargas."""
