# NetCorp · Red empresarial multisede en Cisco

[![Validar red](https://github.com/0scar07/netcorp-cisco/actions/workflows/validar.yml/badge.svg)](https://github.com/0scar07/netcorp-cisco/actions/workflows/validar.yml)
![Cisco IOS](https://img.shields.io/badge/Cisco-IOS-1BA0D7?logo=cisco&logoColor=white)
![Packet Tracer](https://img.shields.io/badge/Packet%20Tracer-8.2-049FD9)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Licencia MIT](https://img.shields.io/badge/licencia-MIT-green)

Diseño, implementación y validación de la red de **NetCorp**, una empresa ficticia con una sede central, dos sucursales y dos proveedores de Internet. Todo está montado en Cisco Packet Tracer y las configuraciones de los equipos **no se escriben a mano**: salen de un inventario en YAML, se generan con plantillas Jinja2 y se validan con pruebas automáticas en cada push.

> **Qué demuestra este proyecto:** diseño jerárquico de campus, alta disponibilidad en capa 2 y capa 3, enrutamiento interno y externo, VPN entre sedes, seguridad por capas y una forma de trabajar de "red como código" con control de versiones e integración continua.

---

## Topología

![Topología de NetCorp](diagramas/topologia.png)

<details>
<summary>Versión en Mermaid (se puede editar como texto)</summary>

```mermaid
flowchart TB
    subgraph NET["Internet simulada"]
        ISP1["ISP1 · AS 65001"]
        ISP2["ISP2 · AS 65002"]
        WEBX[("INTERNET-WEB<br/>192.0.2.10")]
        ISP1 ---|"eBGP · serial"| ISP2
        ISP1 --- WEBX
    end

    subgraph HQ["Sede central · 10.10.0.0/16 · AS 65100"]
        EDGE1["HQ-EDGE1<br/>borde principal"]
        EDGE2["HQ-EDGE2<br/>borde de respaldo"]
        DSW1["HQ-DSW1<br/>multicapa · HSRP"]
        DSW2["HQ-DSW2<br/>multicapa · HSRP"]
        ASW1["HQ-ASW1<br/>Administración · Ventas"]
        ASW2["HQ-ASW2<br/>TI · Wi-Fi invitados"]
        ASW3["HQ-ASW3<br/>Servidores"]
        EDGE1 --- DSW1 & DSW2
        EDGE2 --- DSW1 & DSW2
        DSW1 ===|"Po1 · LACP"| DSW2
        DSW1 --- ASW1 & ASW2 & ASW3
        DSW2 --- ASW1 & ASW2 & ASW3
    end

    subgraph SN["Sucursal Norte · 10.20.0.0/16"]
        R1["BR1-RTR"] --- S1["BR1-SW"]
    end
    subgraph SS["Sucursal Sur · 10.30.0.0/16"]
        R2["BR2-RTR"] --- S2["BR2-SW"]
    end

    EDGE1 ---|eBGP| ISP1
    EDGE2 ---|eBGP| ISP2
    R1 --- ISP1
    R2 --- ISP2
    EDGE1 -. "GRE/IPsec principal" .- R1
    EDGE1 -. "GRE/IPsec principal" .- R2
    EDGE2 -. "GRE/IPsec respaldo" .- R1
    EDGE2 -. "GRE/IPsec respaldo" .- R2
```

</details>

13 equipos de red, 6 servidores, 2 sitios remotos y 33 cables. El detalle puerto por puerto está en [docs/generado/cableado.md](docs/generado/cableado.md).

## Qué incluye

| Área | Tecnologías |
|------|-------------|
| **Conmutación** | VLANs por departamento, troncales 802.1Q con VLAN nativa sin uso, Rapid PVST+, EtherChannel LACP, VTP transparente |
| **Alta disponibilidad** | HSRPv2 con balanceo de carga entre los dos switches de distribución, raíz de STP alineada con el HSRP activo, doble router de borde, doble ISP y túneles de respaldo |
| **Enrutamiento interno** | OSPF multiárea (área 0 en la sede y los túneles, áreas 1 y 2 en las sucursales), resumen de rutas en los ABR, autenticación MD5 y `passive-interface` por defecto |
| **Enrutamiento externo** | eBGP con dos proveedores, publicación del bloque público propio y ruta por defecto principal y de respaldo inyectada en OSPF |
| **VPN** | GRE sobre IPsec (IKEv1, AES-256, SHA, DH grupo 5) en estrella con doble hub, para que OSPF viaje cifrado entre sedes |
| **Servicios** | NAT/PAT, NAT estática para publicar el servidor web, DHCP centralizado con relay y DHCP local en sucursales, DNS, NTP, Syslog, TFTP y SNMP |
| **Seguridad** | SSH v2 solo desde redes de gestión, AAA con TACACS+ y respaldo local, port-security, DHCP snooping, BPDU Guard, ACL para invitados y para la granja de servidores, puertos sin uso apagados |
| **Red como código** | Inventario YAML, plantillas Jinja2, generador en Python, 145 pruebas con pytest y CI en GitHub Actions |

## Red como código

```mermaid
flowchart LR
    A["inventario/red.yml<br/>única fuente de verdad"] --> B["scripts/generar.py<br/>+ plantillas Jinja2"]
    B --> C["configs/*.txt<br/>una por equipo"]
    B --> D["docs/generado/*.md<br/>cableado y direccionamiento"]
    C & D --> E["pytest + GitHub Actions"]
    C --> F["Packet Tracer<br/>se pegan en la CLI"]
```

Cambiar la red es cambiar el inventario. El generador reescribe las configuraciones y la documentación, y la CI falla si alguien edita una configuración a mano o deja la documentación desactualizada. Las pruebas revisan cosas como:

- que no haya IP repetidas ni VLANs que se solapen,
- que los dos extremos de cada cable estén en la misma subred,
- que cada túnel tenga su pareja con el mismo costo OSPF y apunte a la WAN correcta,
- que la raíz de STP coincida con el HSRP activo,
- que todos los equipos cumplan la línea base de seguridad (SSH v2, sin Telnet, AAA, ACL de gestión...).

## Estructura

```
netcorp-cisco/
├── inventario/red.yml          # todo el diseño: sitios, VLANs, IPs, equipos y cables
├── plantillas/                 # plantillas Jinja2 por rol (borde, distribución, acceso, sucursal, ISP)
├── scripts/generar.py          # genera configs/ y docs/generado/
├── configs/                    # configuración final de cada equipo, lista para pegar
├── tests/                      # pruebas del diseño y de las configuraciones
├── diagramas/                  # diagrama de topología (SVG en HTML y PNG)
├── docs/
│   ├── 01-diseno.md            # requisitos, decisiones y alta disponibilidad
│   ├── 02-direccionamiento.md  # cómo está pensado el plan de IPs
│   ├── 03-construccion.md      # paso a paso para montarla en Packet Tracer
│   ├── 04-seguridad.md         # controles por plano
│   ├── 05-pruebas.md           # plan de pruebas y de fallos
│   ├── 06-solucion-de-problemas.md
│   └── generado/               # cableado y direccionamiento (no editar a mano)
├── topologia/                  # el archivo .pkt
└── evidencias/                 # capturas de las pruebas
```

## Cómo usarlo

```bash
pip install -r requirements.txt
python scripts/generar.py      # regenera configs/ y docs/generado/
python -m pytest               # valida el diseño y las configuraciones
```

Para montar la red en Packet Tracer sigue [docs/03-construccion.md](docs/03-construccion.md): qué equipos poner, qué módulos agregar, cómo activar las licencias, cómo configurar los servidores y en qué orden pegar cada archivo de `configs/`.

## Documentación

1. [Diseño y decisiones](docs/01-diseno.md)
2. [Plan de direccionamiento](docs/02-direccionamiento.md) · [tablas completas](docs/generado/direccionamiento.md)
3. [Construcción en Packet Tracer](docs/03-construccion.md) · [cableado](docs/generado/cableado.md)
4. [Seguridad](docs/04-seguridad.md)
5. [Plan de pruebas y fallos](docs/05-pruebas.md)
6. [Solución de problemas](docs/06-solucion-de-problemas.md)

## Credenciales

Las claves del inventario son **solo de laboratorio** y están a la vista para que cualquiera pueda reproducir la red. Si reutilizas estas plantillas fuera de Packet Tracer, cámbialas y sácalas del repositorio.

## Próximos pasos

- [ ] IPv6 de doble pila con OSPFv3
- [ ] ACL de entrada en las WAN (solo IKE, ESP, BGP y tráfico de vuelta)
- [ ] SNMPv3 en lugar de SNMPv2c
- [ ] Seguimiento de enlaces en HSRP (`standby track`) cuando el simulador lo permita
- [ ] Segundo enlace a Internet en cada sucursal para eliminar su punto único de fallo
- [ ] Llevar la misma automatización a equipos reales o a Cisco CML con Netmiko o Ansible

## Autor

**Oscar** · [GitHub @0scar07](https://github.com/0scar07)

Proyecto publicado con [licencia MIT](LICENSE).
