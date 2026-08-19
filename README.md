# senamhi-moquegua-downloader

Automatiza la descarga de datos históricos hidrometeorológicos de SENAMHI
(`https://www.senamhi.gob.pe/site/descarga-datos/`) para las estaciones de
Moquegua, sin intentar evadir el captcha del portal.

El script abre un navegador real (Chrome/Brave/Edge, vía [zendriver](https://github.com/cdpdriver/zendriver),
misma lógica de detección que usa [Garúa](https://github.com/danyneyra/senamhi-scraper))
y navega automáticamente a la página de cada estación. Tú resuelves el
captcha y aceptas los términos y condiciones a mano en esa ventana — el
script solo se encarga de moverse entre estaciones y de mover el archivo
descargado a `downloads/`.

## Requisitos

- Python 3.11+
- Google Chrome, Brave o Microsoft Edge instalado (no requiere permisos de administrador)

## Instalación

```bash
pip install -r requirements.txt
cp .env.example .env
# edita .env si tu carpeta de Descargas no es ~/Downloads
```

## Uso

```bash
python run.py
```

Por cada estación de `data/estaciones_moquegua.json`, el navegador abrirá
la página de descarga correspondiente. Resuelve el/los captcha y acepta
los términos y condiciones, haz clic en "Descargar", y presiona ENTER en
la terminal para continuar con la siguiente estación.

## Estructura

- `data/estaciones_moquegua.json` — nombre y código SENAMHI de cada estación.
- `src/senamhi_downloader/browser.py` — detección del navegador (adaptado de Garúa).
- `src/senamhi_downloader/downloader.py` — orquestación del flujo de descarga.
- `downloads/` — archivos descargados (ignorado por git salvo `.gitkeep`).
