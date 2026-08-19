# station-hist

Automatiza la descarga de datos históricos hidrometeorológicos de SENAMHI
para cualquier estación del Perú, vía dos portales distintos de SENAMHI:

- **`run_climatico.py`** — portal [`site/descarga-datos/`](https://www.senamhi.gob.pe/site/descarga-datos/):
  requiere captcha y login. No se intenta evadir el captcha; el script
  automatiza solo la navegación entre estaciones.
- **`run_operativo.py`** — portal `mapas/mapa-estaciones-2/` (el mismo que
  usa [Garúa](https://github.com/danyneyra/senamhi-scraper)): sin captcha
  ni login, completamente automático de principio a fin.

Ambos abren un navegador real (Chrome/Brave/Edge, vía [zendriver](https://github.com/cdpdriver/zendriver)).

## Requisitos

- Python 3.11+
- Google Chrome, Brave o Microsoft Edge instalado (no requiere permisos de administrador)

## Instalación

```bash
git clone https://github.com/Japq91/station-hist.git
cd station-hist
pip install -r requirements.txt
cp .env.example .env
```

## `run_climatico.py` (con captcha)

Incluye `data/estaciones.json` con las 293 estaciones disponibles en este
portal, en 22 departamentos del Perú.

Buscar el código de una estación por nombre:

```bash
python run_climatico.py --search UBINAS
```

Descargar una o más estaciones por código:

```bash
python run_climatico.py --station 000851 --station 000806
```

Descargar todas las estaciones de un departamento:

```bash
python run_climatico.py --dep MOQUEGUA
```

Descargar las estaciones dentro de un rectángulo geográfico (lat1, lat2, lon1, lon2, en cualquier orden).
Usa `=` (no espacio) porque los valores empiezan con `-` y confunden a argparse:

```bash
python run_climatico.py --bbox=-18.5,-16,-71,-70
```

Ver los departamentos disponibles, o diagnosticar el navegador detectado:

```bash
python run_climatico.py --list-departamentos
python run_climatico.py --doctor
```

El navegador abre directo con zoom en el **mapa filtrado por el
departamento de la primera estación de la lista**, y pausa para que
completes el "Ingreso" (acepta términos y condiciones y resuelve el
captcha) — esa sesión se mantiene dentro de la misma pestaña para el resto
de la corrida.

Luego, por cada estación seleccionada, el navegador abre el **mapa filtrado
por el departamento de esa estación** (no un link directo — la página de
descarga solo funciona bien si se llega a ella haciendo clic en el globo,
igual que en el uso manual). Busca el globo de la estación indicada, haz
clic en él, ve a la pestaña "Descarga", resuelve el captcha, acepta los
términos y haz clic en "Descargar" — el archivo se guarda directo en
`downloads/` del proyecto. Presiona ENTER en la terminal para pasar a la
siguiente estación.

## `run_operativo.py` (sin captcha, automático)

Incluye `data_operativo/estaciones.json` con las 1010 estaciones del
registro nacional que usa Garúa (código, nombre, departamento, lat, lon,
alt, tipo, estado). Usa la misma selección por `--station`, `--dep`,
`--search` o `--bbox`, más el rango de años:

```bash
python run_operativo.py --bbox=-18.5,-16,-71,-70
python run_operativo.py --bbox=-18.5,-16,-71,-70 --yeari 2020 --yearf 2024
python run_operativo.py --station 100142 --station 117002
python run_operativo.py --dep MOQUEGUA
```

Por defecto descarga el periodo **2017-2026**; `--yeari`/`--yearf` lo
acotan. No hay login ni captcha que resolver — el navegador solo necesita
pasar la verificación automática de Cloudflare, algo que ya resuelve
zendriver al usar un navegador real. El script recorre las estaciones sin
pausas, seleccionando cada periodo disponible dentro del rango y
capturando la respuesta directamente (sin depender de que el navegador
descargue un archivo). Cada estación genera **un único CSV consolidado**,
nombrado por su código SENAMHI (ej: `100142-2017-2026.csv`) en
`downloads_operativo/`.

## Estructura

- `data/estaciones.json`, `data_operativo/estaciones.json` — metadata de estaciones (código, nombre, departamento, lat, lon[, alt]) de cada portal.
- `src/senamhi_downloader/browser.py` — detección del navegador, compartida por ambos scripts (adaptado de Garúa).
- `src/senamhi_downloader/{stations,cli,downloader}.py` — lógica de `run_climatico.py`.
- `src/senamhi_downloader/operativo/` — lógica de `run_operativo.py` (scraping vía CDP, sin captcha), portada de Garúa.
- `downloads/`, `downloads_operativo/` — archivos descargados de cada portal (ignorados por git salvo `.gitkeep`).
