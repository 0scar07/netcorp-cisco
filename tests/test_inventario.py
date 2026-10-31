"""Comprueba que el diseño del inventario es coherente antes de tocar Packet Tracer."""
import ipaddress
import itertools
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from generar import cargar_inventario, extremo  # noqa: E402

INV = cargar_inventario()
EQUIPOS = INV["dispositivos"]


def interfaces_con_ip(nombre, d):
    """(interfaz, ip_interface) de todas las IP de un equipo, menos las SVI de HQ."""
    for i in d.get("interfaces", []):
        yield i["nombre"], ipaddress.ip_interface(i["ip"])
    if "wan" in d:
        yield d["wan"]["nombre"], ipaddress.ip_interface(d["wan"]["ip"])
    for t in d.get("tuneles", []):
        yield f"Tunnel{t['num']}", ipaddress.ip_interface(t["ip"])
    if "loopback" in d:
        yield "Loopback0", ipaddress.ip_interface(f"{d['loopback']}/32")
    if "gestion" in d:
        yield "Vlan99", ipaddress.ip_interface(d["gestion"])


def todas_las_ip():
    for nombre, d in EQUIPOS.items():
        for interfaz, ip in interfaces_con_ip(nombre, d):
            yield nombre, interfaz, ip
    for nombre, h in INV["hosts"].items():
        if "/" in str(h["ip"]):
            yield nombre, "NIC", ipaddress.ip_interface(h["ip"])


def test_no_hay_ip_repetidas():
    vistas = {}
    for nombre, interfaz, ip in todas_las_ip():
        assert ip.ip not in vistas, f"{ip.ip} está en {vistas.get(ip.ip)} y en {nombre} {interfaz}"
        vistas[ip.ip] = f"{nombre} {interfaz}"


def test_las_vlans_no_se_solapan_y_caben_en_su_sitio():
    redes = []
    for clave, sitio in INV["sitios"].items():
        resumen = ipaddress.ip_network(sitio["resumen"])
        for v in sitio["vlans"]:
            red = ipaddress.ip_network(v["red"])
            assert red.subnet_of(resumen), f"VLAN {v['id']} de {clave} ({red}) no cabe en {resumen}"
            redes.append((f"{clave}/VLAN{v['id']}", red))
    for (a, ra), (b, rb) in itertools.combinations(redes, 2):
        assert not ra.overlaps(rb), f"{a} ({ra}) se solapa con {b} ({rb})"


def test_los_resumenes_de_los_sitios_no_se_solapan():
    resumenes = [ipaddress.ip_network(s["resumen"]) for s in INV["sitios"].values()]
    for a, b in itertools.combinations(resumenes, 2):
        assert not a.overlaps(b)


def test_cada_puerto_se_usa_una_sola_vez():
    vistos = set()
    for a, b, _ in INV["enlaces"]:
        for e in (extremo(a), extremo(b)):
            assert e not in vistos, f"el puerto {e} aparece en dos enlaces"
            vistos.add(e)


def test_los_enlaces_l3_comparten_subred():
    """Si los dos extremos de un cable tienen IP, deben estar en la misma subred."""
    ips = {(n, i): ip for n, i, ip in todas_las_ip()}
    revisados = 0
    for a, b, _ in INV["enlaces"]:
        ea, eb = extremo(a), extremo(b)
        if ea in ips and eb in ips:
            assert ips[ea].network == ips[eb].network, f"{a} y {b} están en subredes distintas"
            revisados += 1
    assert revisados >= 9  # 4 borde-distribución, 4 WAN y el serial entre ISP


def test_las_interfaces_con_ip_tienen_cable():
    cableados = {extremo(x) for a, b, _ in INV["enlaces"] for x in (a, b)}
    for nombre, d in EQUIPOS.items():
        for i in d.get("interfaces", []) + ([d["wan"]] if "wan" in d else []):
            assert (nombre, i["nombre"]) in cableados, f"{nombre} {i['nombre']} no está en 'enlaces'"


@pytest.mark.parametrize("nombre", [n for n, d in EQUIPOS.items() if d.get("tuneles")])
def test_cada_tunel_tiene_su_pareja(nombre):
    d = EQUIPOS[nombre]
    for t in d["tuneles"]:
        otro = EQUIPOS[t["hacia"]]
        assert ipaddress.ip_interface(otro["wan"]["ip"]).ip == ipaddress.ip_address(t["destino"]), \
            f"{nombre} Tunnel{t['num']} apunta a {t['destino']}, que no es la WAN de {t['hacia']}"
        pareja = [p for p in otro["tuneles"] if p["hacia"] == nombre]
        assert len(pareja) == 1, f"{t['hacia']} no tiene un túnel de vuelta hacia {nombre}"
        p = pareja[0]
        assert ipaddress.ip_interface(p["ip"]).network == ipaddress.ip_interface(t["ip"]).network
        assert p["costo"] == t["costo"], "el costo OSPF debe ser igual en los dos extremos"


def test_hsrp_activo_es_un_switch_de_distribucion():
    distribucion = {n for n, d in EQUIPOS.items() if d["rol"] == "distribucion"}
    for v in INV["sitios"]["HQ"]["vlans"]:
        assert v["activo"] in distribucion


def test_hsrp_reparte_la_carga_entre_los_dos_switches():
    activos = {v["activo"] for v in INV["sitios"]["HQ"]["vlans"]}
    assert len(activos) == 2


def test_los_servidores_estan_en_la_vlan_de_servidores():
    red = ipaddress.ip_network(next(v["red"] for v in INV["sitios"]["HQ"]["vlans"] if v["nombre"] == "SERVIDORES"))
    for servicio, ip in INV["global"]["servidores"].items():
        assert ipaddress.ip_address(ip) in red, f"el servidor {servicio} ({ip}) está fuera de {red}"


def test_la_ip_de_gestion_esta_en_la_vlan_de_gestion():
    for nombre, d in EQUIPOS.items():
        if "gestion" not in d:
            continue
        sitio = INV["sitios"][d["sitio"]]
        red = ipaddress.ip_network(next(v["red"] for v in sitio["vlans"] if v["nombre"] == "GESTION"))
        assert ipaddress.ip_interface(d["gestion"]).ip in red


def test_credenciales_cumplen_los_minimos():
    c = INV["global"]["credenciales"]
    assert len(c["enable_secret"]) >= 10 and len(c["clave_usuario"]) >= 10  # security passwords min-length 10
    assert len(c["ospf_md5"]) <= 16, "IOS solo acepta claves MD5 de OSPF de hasta 16 caracteres"
    for valor in c.values():
        assert "?" not in valor, "el signo ? abre la ayuda de IOS al pegar"
