#!/usr/bin/env python3
"""Genera las configuraciones y la documentación de NetCorp desde inventario/red.yml.

Uso:
    python scripts/generar.py           # escribe configs/ y docs/generado/
    python scripts/generar.py --check   # falla si algo generado no está al día (lo usa la CI)
"""
from __future__ import annotations

import argparse
import ipaddress
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

RAIZ = Path(__file__).resolve().parent.parent
INVENTARIO = RAIZ / "inventario" / "red.yml"
PLANTILLAS = RAIZ / "plantillas"
SALIDA_CONFIGS = RAIZ / "configs"
SALIDA_DOCS = RAIZ / "docs" / "generado"

ABREVIATURAS = {
    "GigabitEthernet": "Gi",
    "FastEthernet": "Fa",
    "Serial": "Se",
    "Port-channel": "Po",
    "Tunnel": "Tu",
    "Loopback": "Lo",
}


# ---------------------------------------------------------------- filtros

def ip(cidr: str) -> str:
    """10.10.10.2/24 -> 10.10.10.2"""
    return str(ipaddress.ip_interface(cidr).ip)


def mascara(cidr: str) -> str:
    """10.10.10.0/24 -> 255.255.255.0"""
    return str(ipaddress.ip_interface(cidr).netmask)


def wildcard(cidr: str) -> str:
    """10.10.0.0/16 -> 0.0.255.255"""
    return str(ipaddress.ip_interface(cidr).hostmask)


def red(cidr: str) -> str:
    """10.10.10.2/24 -> 10.10.10.0"""
    return str(ipaddress.ip_interface(cidr).network.network_address)


def ip_mascara(cidr: str) -> str:
    """10.255.1.1/30 -> '10.255.1.1 255.255.255.252'"""
    return f"{ip(cidr)} {mascara(cidr)}"


def host(cidr: str, n: int) -> str:
    """Host número n de la red: host('10.10.10.0/24', 1) -> 10.10.10.1"""
    return str(ipaddress.ip_network(cidr, strict=False)[n])


def corto(interfaz: str) -> str:
    """GigabitEthernet1/0/1 -> Gi1/0/1"""
    for largo, abreviado in ABREVIATURAS.items():
        if interfaz.startswith(largo):
            return abreviado + interfaz[len(largo):]
    return interfaz


# ---------------------------------------------------------------- inventario

def cargar_inventario(ruta: Path = INVENTARIO) -> dict:
    with open(ruta, encoding="utf-8") as f:
        return yaml.safe_load(f)


def extremo(texto: str) -> tuple[str, str]:
    equipo, interfaz = texto.split(":", 1)
    return equipo.strip(), interfaz.strip()


def mapa_vecinos(inv: dict) -> dict[tuple[str, str], tuple[str, str]]:
    """(equipo, interfaz) -> (equipo vecino, interfaz vecina), a partir de los enlaces."""
    vecinos = {}
    for a, b, _cable in inv["enlaces"]:
        ea, eb = extremo(a), extremo(b)
        vecinos[ea] = eb
        vecinos[eb] = ea
    return vecinos


def crear_entorno(inv: dict) -> Environment:
    vecinos = mapa_vecinos(inv)

    def hacia(equipo: str, interfaz: str) -> str:
        equipo_b, interfaz_b = vecinos[(equipo, interfaz)]
        return f"{equipo_b} {corto(interfaz_b)}"

    env = Environment(
        loader=FileSystemLoader(PLANTILLAS),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.filters.update(ip=ip, mascara=mascara, wildcard=wildcard, red=red,
                       ip_mascara=ip_mascara, host=host, corto=corto)
    env.globals.update(hacia=hacia, inv=inv, g=inv["global"],
                       c=inv["global"]["credenciales"], s=inv["global"]["servidores"],
                       ve=inv["global"]["vlans_especiales"])
    return env


def renderizar(inv: dict) -> dict[Path, str]:
    """Devuelve {ruta de salida: contenido} de todo lo que genera el proyecto."""
    env = crear_entorno(inv)
    salida: dict[Path, str] = {}

    for nombre, d in inv["dispositivos"].items():
        sitio = inv["sitios"].get(d["sitio"], {"vlans": []})
        plantilla = env.get_template(f"{d['rol']}.j2")
        salida[SALIDA_CONFIGS / f"{nombre}.txt"] = plantilla.render(nombre=nombre, d=d, sitio=sitio)

    for doc in ("cableado.md", "direccionamiento.md"):
        plantilla = env.get_template(f"docs/{doc}.j2")
        salida[SALIDA_DOCS / doc] = plantilla.render()

    return salida


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="no escribe nada; falla si los archivos generados no coinciden con el inventario")
    args = parser.parse_args()

    salida = renderizar(cargar_inventario())

    if args.check:
        desactualizados = [
            ruta for ruta, contenido in salida.items()
            if not ruta.exists() or ruta.read_text(encoding="utf-8").replace("\r\n", "\n") != contenido
        ]
        for ruta in desactualizados:
            print(f"desactualizado: {ruta.relative_to(RAIZ)}")
        if desactualizados:
            print("Ejecuta 'python scripts/generar.py' y sube los cambios.")
            return 1
        print(f"OK: {len(salida)} archivos generados están al día.")
        return 0

    for ruta, contenido in salida.items():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(contenido, encoding="utf-8", newline="\n")
        print(f"generado: {ruta.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
