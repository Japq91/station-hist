# station-hist

Un par de scripts en Python para automatizar la descarga de datos históricos hidrometeorológicos del SENAMHI (Perú). Como meteorólogo, descargar estos datos manualmente estación por estación es tedioso, así que armé este proyecto para agilizar el proceso.

El SENAMHI tiene dos portales distintos, por lo que el repositorio se divide en dos enfoques:

- **`run_climatico.py`**: para el portal de [Descarga de Datos](https://www.senamhi.gob.pe/site/descarga-datos/). Requiere login y captcha. El script automatiza la navegación y el filtrado entre estaciones, pero la validación humana inicial hay que hacerla a mano (correo ingreso y para cada estación).
- **`run_operativo.py`**: para el portal del [Mapa de Estaciones](https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/). 95% automático, sin captcha ni login (usa la misma ruta que [Garúa](https://github.com/danyneyra/senamhi-scraper)). Sin embargo, este requiere aceptar un captcha en cada vez que se cambia de estación.

Ambos usan [zendriver](https://github.com/cdpdriver/zendriver) por detrás para levantar una instancia real de Chrome, Brave o Edge.

## Requisitos

- Conda (Miniconda o Anaconda)
- Chrome, Brave o Edge instalado (no requiere permisos de administrador)

## Instalación

Clona el repositorio y crea el ambiente de conda (`getdata`), que ya incluye Python 3.11 y las dependencias necesarias:

```bash
git clone https://github.com/Japq91/station-hist.git
cd station-hist
conda env create -f environment.yml
conda activate getdata
cp .env.example .env
```
## 1. Descarga del portal climático (semi-automático)

Ejecuta `run_climatico.py`. El repositorio incluye la metadata de 293 estaciones en `data/estaciones.json`.

**Ejemplos de uso:**


```bash
#Buscar el código de una estación por nombre:
python run_climatico.py --search UBINAS
#Descargar por código (soporta varias estaciones):
python run_climatico.py --station 000851 --station 000806
#Descargar un departamento completo:
python run_climatico.py --dep MOQUEGUA
#Descargar por rectángulo geográfico (lat1, lat2, lon1, lon2). Usa `=` para que argparse no confunda los signos negativos con otra opción:
python run_climatico.py --bbox=-18.5,-16,-71,-70
```

Ver los departamentos disponibles, o diagnosticar el navegador detectado:
```bash
python run_climatico.py --list-departamentos
python run_climatico.py --doctor
```

**Flujo de ejecución:**
Al iniciar, el script abre el navegador centrado en el mapa del departamento correspondiente a la primera estación. 
La ejecución hace una pausa para que inicies sesión, aceptes los términos y resuelvas el captcha manualmente. 
Una vez que descargas el primer archivo, presionas ENTER en la terminal y el script avanza a la siguiente estación, manteniendo la sesión activa. Los archivos quedan en `downloads/`.

## 2. Descarga del portal operativo (100% automático)

Ejecuta `run_operativo.py`. Incluye la metadata de 1010 estaciones en `data_operativo/estaciones.json`. Soporta los mismos filtros geográficos y de búsqueda, más el rango de años.

**Ejemplos de uso:**
```bash
python run_operativo.py --station 100142 --station 117002
python run_operativo.py --bbox=-18.5,-16,-71,-70 --yeari 2020 --yearf 2024
```

Si no especificas años, descarga por defecto el periodo 2017-2026.

**Flujo de ejecución:**
El proceso es completamente desatendido. Al usar un navegador real, se pasa sin problemas la verificación de Cloudflare. El script recorre las estaciones indicadas, extrae los datos interceptando las respuestas directamente (sin depender de que el navegador descargue un archivo) y consolida los resultados. Cada estación genera un único CSV, nombrado por su código SENAMHI (ej: `100142-2017-2026.csv`), en `downloads_operativo/`.

## Estructura del proyecto

- `environment.yml`: ambiente conda `getdata` con las dependencias de ambos scripts.
- `data/` y `data_operativo/`: JSON con la metadata de las estaciones (coordenadas, códigos, departamentos) de cada portal.
- `src/senamhi_downloader/`: código fuente. Contiene la detección del navegador (`browser.py`), la CLI y la lógica de scraping de cada portal (`operativo/` para el segundo).
- `downloads/` y `downloads_operativo/`: carpetas de salida de los datos (ignoradas por git).
