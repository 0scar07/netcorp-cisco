# 2. Plan de direccionamiento

Las tablas completas, con cada interfaz y cada equipo, se generan solas en [generado/direccionamiento.md](generado/direccionamiento.md). Aquí está la lógica detrás de ellas.

## La regla: `10.<sitio>.<vlan>.0/24`

| Segundo octeto | Sitio |
|----------------|-------|
| 10 | Sede central |
| 20 | Sucursal Norte |
| 30 | Sucursal Sur |
| 255 | Infraestructura (enlaces punto a punto y loopbacks) |

El tercer octeto es el número de VLAN. `10.20.10.0/24` se lee "sitio 20, VLAN 10": Administración de la Sucursal Norte. Con esta regla:

- cualquier IP dice de qué sitio y departamento es sin mirar una tabla,
- cada sitio se resume en una sola ruta `/16`, que es lo que anuncian los ABR,
- una sucursal nueva solo necesita el siguiente número libre (`10.40.0.0/16`).

## Dentro de cada VLAN de la sede

| Host | Uso |
|------|-----|
| `.1` | IP virtual de HSRP (gateway de los usuarios) |
| `.2` | SVI de HQ-DSW1 |
| `.3` | SVI de HQ-DSW2 |
| `.10` - `.50` | Reservado para equipos con IP fija (servidores, switches, impresoras) |
| `.51` - `.200` | Pool de DHCP |

En las sucursales el gateway es la `.1` del router, se excluyen de DHCP las direcciones `.1` a `.20` y el resto se reparte.

## Infraestructura

| Bloque | Uso |
|--------|-----|
| `10.255.1.0/28` | Cuatro enlaces `/30` entre los routers de borde y los switches de distribución |
| `10.255.255.0/24` | Loopbacks `/32` (router ID de OSPF) |
| `172.16.1.0/24` | Túneles principales (HQ-EDGE1) |
| `172.16.2.0/24` | Túneles de respaldo (HQ-EDGE2) |

## Direcciones públicas

Se usan los rangos que la [RFC 5737](https://www.rfc-editor.org/rfc/rfc5737) reserva para documentación, para que el laboratorio nunca choque con direcciones reales:

| Bloque | Uso |
|--------|-----|
| `198.51.100.0/24` (TEST-NET-2) | Enlaces con los ISP y entre ISP |
| `203.0.113.0/24` (TEST-NET-3) | Bloque público de NetCorp anunciado por BGP |
| `192.0.2.0/24` (TEST-NET-1) | Servidor de "Internet" |

## Números de sistema autónomo

| AS | Quién |
|----|-------|
| 65100 | NetCorp |
| 65001 | ISP1 |
| 65002 | ISP2 |

Son ASN privados (64512-65534), los que corresponden a un laboratorio.
