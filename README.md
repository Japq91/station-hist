# station-hist

Automatiza la descarga de datos históricos hidrometeorológicos de SENAMHI
(`https://www.senamhi.gob.pe/site/descarga-datos/`) para cualquier estación
del Perú, sin intentar evadir el captcha del portal.

El script abre un navegador real (Chrome/Brave/Edge, vía [zendriver](https://github.com/cdpdriver/zendriver),
misma lógica de detección que usa [Garúa](https://github.com/danyneyra/senamhi-scraper))
y navega automáticamente a la página de cada estación que elijas. Tú
resuelves el captcha y aceptas los términos y condiciones a mano en esa
ventana — el script solo se encarga de moverse entre estaciones y de mover
el archivo descargado a `downloads/`.

Incluye `data/estaciones.json` con las 293 estaciones disponibles en el
portal, en 22 departamentos del Perú.

## Requisitos

- Python 3.11+
- Google Chrome, Brave o Microsoft Edge instalado (no requiere permisos de administrador)

## Instalación

```bash
git clone https://github.com/Japq91/station-hist.git
cd station-hist
pip install -r requirements.txt
cp .env.example .env
# edita .env si tu carpeta de Descargas no es ~/Downloads
```

## Uso

Buscar el código de una estación por nombre:

```bash
python run.py --search UBINAS
```

Descargar una o más estaciones por código:

```bash
python run.py --station 000851 --station 000806
```

Descargar todas las estaciones de un departamento:

```bash
python run.py --dep MOQUEGUA
```

Descargar las estaciones dentro de un rectángulo geográfico (lat1, lat2, lon1, lon2, en cualquier orden).
Usa `=` (no espacio) porque los valores empiezan con `-` y confunden a argparse:

```bash
python run.py --bbox=-18.5,-16,-71,-70
```

Ver los departamentos disponibles:

```bash
python run.py --list-departamentos
```

Diagnosticar qué navegador detecta el script:

```bash
python run.py --doctor
```

El primer navegador abierto pausa para que completes el "Ingreso" (acepta
términos y condiciones y resuelve el captcha) — esa sesión se mantiene para
el resto de la corrida. Luego, por cada estación seleccionada, el navegador
abre su página de descarga; resuelve el captcha, acepta los términos y haz
clic en "Descargar". En la terminal verás un menú:

```
[1] Aun no he terminado (esperar)
[2] Ya descargue -> mover archivo y continuar
[3] Saltar esta estacion
```

Elige `2` una vez que el archivo ya se descargó a tu carpeta de Descargas —
el script lo mueve a `downloads/` del proyecto y pasa a la siguiente
estación automáticamente.

## Estructura

- `data/estaciones.json` — nombre, código y departamento de cada estación disponible.
- `src/senamhi_downloader/browser.py` — detección del navegador (adaptado de Garúa).
- `src/senamhi_downloader/stations.py` — búsqueda/filtrado de estaciones.
- `src/senamhi_downloader/cli.py` — interfaz de línea de comandos.
- `src/senamhi_downloader/downloader.py` — orquestación del flujo de descarga.
- `downloads/` — archivos descargados (ignorado por git salvo `.gitkeep`).
