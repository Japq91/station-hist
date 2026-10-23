# station-hist

Un par de scripts en Python para automatizar la descarga de datos históricos hidrometeorológicos del SENAMHI (Perú). Como meteorólogo, descargar estos datos manualmente estación por estación es tedioso, así que armé este proyecto para agilizar el proceso.

El SENAMHI tiene dos portales distintos, por lo que el repositorio se divide en dos enfoques:

- **`run_climatico.py`**: para el portal de [Descarga de Datos](https://www.senamhi.gob.pe/site/descarga-datos/). Requiere login y captcha. El script automatiza la navegación y el filtrado entre estaciones, pero la validación humana inicial hay que hacerla a mano (correo ingreso y para cada estación).
- **`run_operativo.py`**: para el portal del [Mapa de Estaciones](https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/). Casi automático, sin login (usa la misma ruta que [Garúa](https://github.com/danyneyra/senamhi-scraper)). Lo único manual es la verificación de Cloudflare, que a veces aparece al cambiar de estación.

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

## 2. Descarga del portal operativo (casi automático)

Ejecuta `run_operativo.py`. Incluye la metadata de 1010 estaciones en `data_operativo/estaciones.json`. Soporta los mismos filtros geográficos y de búsqueda, más el rango de años.

**Ejemplos de uso:**
```bash
#Buscar el código de una estación por nombre (no abre el navegador):
python run_operativo.py --search "CAMPO DE MARTE"
#Descargar por código, una o varias estaciones:
python run_operativo.py --station 100142 --station 117002
#Por departamento o por rectángulo geográfico, con rango de años:
python run_operativo.py --dep MOQUEGUA --yeari 2024 --yearf 2024
python run_operativo.py --bbox=-18.5,-16,-71,-70 --yeari 2020 --yearf 2024
```

Ojo con los nombres repetidos: muchas estaciones aparecen dos veces, una convencional y otra automática (por ejemplo, Campo de Marte es `112171` convencional y `112181` automática, con datos cada hora). Fíjate en la categoría (`EMA` = automática) antes de descargar, porque las columnas del CSV cambian.

Si no especificas años, descarga por defecto el periodo 2017-2026.

**Flujo de ejecución:**
Al usar un navegador real, la mayoría de las veces se pasa la verificación de Cloudflare sin hacer nada. La primera estación arranca sola; desde la segunda, el script hace una pausa al abrir cada estación: si en el navegador apareció la casilla de Cloudflare, la marcas y presionas ENTER en la terminal (si no apareció, solo ENTER). Sin esa pausa, los periodos de una estación bloqueada se perdían sin aviso.

El script recorre las estaciones indicadas, extrae los datos interceptando las respuestas directamente (sin depender de que el navegador descargue un archivo) y consolida los resultados. Cada estación genera un único CSV, nombrado por su código SENAMHI (ej: `100142-2017-2026.csv`), en `downloads_operativo/`.

**Estaciones con sensores de menos.** Algunas automáticas no miden todo (por ejemplo Ceres, `112278`, no tiene humedad). El encabezado del CSV se arma con las columnas que trae la tabla de SENAMHI, así que esas estaciones salen con una columna menos y la terminal lo avisa (`Columnas ausentes en esta estacion: Humedad (%)`). Si alguna fila no calza con el encabezado, también avisa al guardar: en ese caso revisa el CSV, porque los valores pueden estar corridos. Igual conviene contar las filas, porque las horas sin registro no aparecen.

## Estructura del proyecto

- `environment.yml`: ambiente conda `getdata` con las dependencias de ambos scripts.
- `data/` y `data_operativo/`: JSON con la metadata de las estaciones (coordenadas, códigos, departamentos) de cada portal.
- `src/senamhi_downloader/`: código fuente. Contiene la detección del navegador (`browser.py`), la CLI y la lógica de scraping de cada portal (`operativo/` para el segundo).
- `downloads/` y `downloads_operativo/`: carpetas de salida de los datos (ignoradas por git).
