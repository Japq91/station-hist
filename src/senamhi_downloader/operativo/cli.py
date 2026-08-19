import argparse
import asyncio

from senamhi_downloader.operativo import settings
from senamhi_downloader.operativo.scraper import download_all
from senamhi_downloader.operativo.stations import (
    filter_by_bbox,
    filter_by_department,
    find_by_code,
    list_departments,
    search_by_name,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_operativo.py",
        description=(
            "Descarga datos historicos de SENAMHI via el portal operativo "
            "(mapa-estaciones-2, sin captcha) para una o mas estaciones del Peru."
        ),
    )
    parser.add_argument(
        "--station", "-s", action="append", metavar="CODIGO",
        help="Codigo de estacion a descargar. Repetible: -s 100142 -s 117002",
    )
    parser.add_argument(
        "--dep", "--departamento", dest="departamento", metavar="DEPARTAMENTO",
        help="Descarga todas las estaciones de un departamento (ej: MOQUEGUA)",
    )
    parser.add_argument(
        "--search", metavar="QUERY",
        help="Busca estaciones por nombre y solo las lista (no descarga)",
    )
    parser.add_argument(
        "--bbox", metavar="LAT1,LAT2,LON1,LON2",
        help=(
            "Descarga las estaciones dentro de un rectangulo geografico. "
            "Usa '=' porque los valores son negativos: --bbox=-18.5,-16,-71,-70"
        ),
    )
    parser.add_argument(
        "--yeari", type=int, default=settings.YEAR_DEFAULT_START,
        help=f"Anio inicial (default: {settings.YEAR_DEFAULT_START})",
    )
    parser.add_argument(
        "--yearf", type=int, default=settings.YEAR_DEFAULT_END,
        help=f"Anio final (default: {settings.YEAR_DEFAULT_END})",
    )
    parser.add_argument(
        "--list-departamentos", action="store_true",
        help="Lista los departamentos disponibles y sale",
    )
    parser.add_argument(
        "--doctor", action="store_true",
        help="Muestra el navegador detectado (Chrome/Brave/Edge) y sale",
    )
    return parser


def _print_stations(stations: list[dict]) -> None:
    for s in stations:
        print(f"  {s['codigo']:>8}  {s['nombre']:<30} {s['departamento']}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.doctor:
        from senamhi_downloader.browser import check_browser

        result = check_browser()
        print(f"ok:      {result.ok}")
        print(f"path:    {result.path}")
        print(f"source:  {result.source}")
        print(f"message: {result.message}")
        return

    if args.list_departamentos:
        for dep in list_departments():
            print(dep)
        return

    if args.search:
        matches = search_by_name(args.search)
        if not matches:
            print(f"Sin resultados para '{args.search}'")
            return
        print(f"{len(matches)} resultado(s):")
        _print_stations(matches)
        return

    if args.yearf < args.yeari:
        parser.error("--yearf no puede ser menor que --yeari")

    stations: list[dict] = []
    if args.station:
        for codigo in args.station:
            station = find_by_code(codigo)
            if station is None:
                print(f"[!] Codigo no encontrado: {codigo}")
                continue
            stations.append(station)

    if args.departamento:
        found = filter_by_department(args.departamento)
        if not found:
            print(f"[!] Sin estaciones para el departamento: {args.departamento}")
        stations.extend(found)

    if args.bbox:
        parts = [p.strip() for p in args.bbox.split(",")]
        if len(parts) != 4:
            parser.error("--bbox debe tener 4 numeros separados por coma: LAT1,LAT2,LON1,LON2")
        try:
            lat1, lat2, lon1, lon2 = (float(p) for p in parts)
        except ValueError:
            parser.error("--bbox debe tener 4 numeros separados por coma: LAT1,LAT2,LON1,LON2")
        found = filter_by_bbox(lat1, lat2, lon1, lon2)
        if not found:
            print(f"[!] Sin estaciones dentro del rectangulo: {args.bbox}")
        stations.extend(found)

    seen_codes: set[str] = set()
    deduped: list[dict] = []
    for s in stations:
        if s["codigo"] in seen_codes:
            continue
        seen_codes.add(s["codigo"])
        deduped.append(s)
    stations = deduped

    if not stations:
        parser.print_help()
        print(
            "\nEjemplos:\n"
            "  python run_operativo.py --search UBINAS\n"
            "  python run_operativo.py --station 100142 --station 117002\n"
            "  python run_operativo.py --dep MOQUEGUA\n"
            "  python run_operativo.py --bbox=-18.5,-16,-71,-70\n"
            "  python run_operativo.py --bbox=-18.5,-16,-71,-70 --yeari 2020 --yearf 2024\n"
        )
        return

    print(f"Se descargaran {len(stations)} estacion(es), periodo {args.yeari}-{args.yearf}:")
    _print_stations(stations)
    asyncio.run(download_all(stations, args.yeari, args.yearf))


if __name__ == "__main__":
    main()
