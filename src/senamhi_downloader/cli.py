import argparse
import asyncio

from senamhi_downloader.downloader import download_all
from senamhi_downloader.stations import (
    filter_by_department,
    find_by_code,
    list_departments,
    search_by_name,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run.py",
        description=(
            "Descarga datos historicos de SENAMHI "
            "(site/descarga-datos) para una o mas estaciones del Peru."
        ),
    )
    parser.add_argument(
        "--station", "-s", action="append", metavar="CODIGO",
        help="Codigo de estacion a descargar. Repetible: -s 000851 -s 000806",
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
        print(f"  {s['codigo']:>8}  {s['name']:<30} {s['departamento']}")


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

    if not stations:
        parser.print_help()
        print(
            "\nEjemplos:\n"
            "  python run.py --search UBINAS\n"
            "  python run.py --station 000851 --station 000806\n"
            "  python run.py --dep MOQUEGUA\n"
            "  python run.py --list-departamentos\n"
        )
        return

    print(f"Se descargaran {len(stations)} estacion(es):")
    _print_stations(stations)
    asyncio.run(download_all(stations))


if __name__ == "__main__":
    main()
