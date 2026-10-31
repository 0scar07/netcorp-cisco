"""Comprueba las configuraciones generadas: que estén al día y que cumplan la línea base de seguridad."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from generar import SALIDA_CONFIGS, cargar_inventario, renderizar  # noqa: E402

INV = cargar_inventario()
GENERADO = renderizar(INV)
CONFIGS = {ruta.stem: texto for ruta, texto in GENERADO.items() if ruta.parent == SALIDA_CONFIGS}
PROPIOS = [n for n, d in INV["dispositivos"].items() if d["rol"] != "isp"]
ROUTERS_VPN = [n for n, d in INV["dispositivos"].items() if d.get("tuneles")]


def test_hay_una_config_por_equipo():
    assert set(CONFIGS) == set(INV["dispositivos"])


@pytest.mark.parametrize("ruta", sorted(GENERADO), ids=lambda r: r.name)
def test_los_archivos_del_repo_estan_al_dia(ruta):
    assert ruta.exists(), f"falta {ruta.name}: ejecuta python scripts/generar.py"
    assert ruta.read_text(encoding="utf-8").replace("\r\n", "\n") == GENERADO[ruta], \
        f"{ruta.name} no coincide con el inventario: ejecuta python scripts/generar.py"


@pytest.mark.parametrize("nombre", PROPIOS)
@pytest.mark.parametrize("linea", [
    "service password-encryption",
    "ip ssh version 2",
    " transport input ssh",
    " access-class GESTION-SSH in",
    "aaa authentication login default group tacacs+ local",
    "login block-for 120 attempts 3 within 60",
    "security passwords min-length 10",
])
def test_linea_base_de_seguridad(nombre, linea):
    assert linea in CONFIGS[nombre].splitlines()


@pytest.mark.parametrize("nombre", CONFIGS)
def test_sin_telnet_ni_claves_en_claro(nombre):
    texto = CONFIGS[nombre]
    assert "transport input telnet" not in texto
    assert "transport input all" not in texto
    assert "enable password" not in texto


@pytest.mark.parametrize("nombre", CONFIGS)
def test_termina_guardando(nombre):
    assert CONFIGS[nombre].rstrip().endswith("end\nwrite memory")


@pytest.mark.parametrize("nombre", ROUTERS_VPN)
def test_cada_tunel_tiene_ipsec(nombre):
    texto = CONFIGS[nombre]
    for t in INV["dispositivos"][nombre]["tuneles"]:
        assert f"set peer {t['destino']}" in texto
        assert f"tunnel destination {t['destino']}" in texto
    assert f" crypto map {INV['global']['vpn']['crypto_map']}" in texto


@pytest.mark.parametrize("nombre", [n for n, d in INV["dispositivos"].items() if d["rol"] == "acceso"])
def test_puertos_de_acceso_protegidos(nombre):
    texto = CONFIGS[nombre]
    assert texto.count("spanning-tree bpduguard enable") == len(INV["dispositivos"][nombre]["acceso"])
    assert "ip dhcp snooping trust" in texto
    assert " switchport access vlan 999" in texto


@pytest.mark.parametrize("nombre", [n for n, d in INV["dispositivos"].items() if d["rol"] == "distribucion"])
def test_stp_alineado_con_hsrp(nombre):
    texto = CONFIGS[nombre].splitlines()
    activas = [str(v["id"]) for v in INV["sitios"]["HQ"]["vlans"] if v["activo"] == nombre]
    assert f"spanning-tree vlan {','.join(activas)} root primary" in texto
    for vlan in activas:
        assert f" standby {vlan} priority 110" in texto
