# Plan de direccionamiento

> Generado por `scripts/generar.py` desde `inventario/red.yml`. No editar a mano.

## Bloques por sitio

| Sitio | Nombre | Bloque resumido |
|-------|--------|-----------------|
| HQ | Sede central | `10.10.0.0/16` |
| BR1 | Sucursal Norte | `10.20.0.0/16` |
| BR2 | Sucursal Sur | `10.30.0.0/16` |
| WAN | Enlaces públicos (TEST-NET-2) | `198.51.100.0/24` |
| PUB | Bloque público de NetCorp (TEST-NET-3) | `203.0.113.0/24` |
| VPN | Túneles GRE | `172.16.0.0/16` |
| INFRA | Enlaces internos y loopbacks | `10.255.0.0/16` |

## VLANs · Sede central (HQ)

| VLAN | Nombre | Red | Gateway (VIP HSRP) | HQ-DSW1 | HQ-DSW2 | HSRP activo | DHCP |
|------|--------|-----|--------------------|---------|---------|-------------|------|
| 10 | ADMINISTRACION | `10.10.10.0/24` | 10.10.10.1 | 10.10.10.2 | 10.10.10.3 | HQ-DSW1 | SRV-DHCP (relay) |
| 20 | VENTAS | `10.10.20.0/24` | 10.10.20.1 | 10.10.20.2 | 10.10.20.3 | HQ-DSW2 | SRV-DHCP (relay) |
| 30 | TI | `10.10.30.0/24` | 10.10.30.1 | 10.10.30.2 | 10.10.30.3 | HQ-DSW1 | SRV-DHCP (relay) |
| 40 | INVITADOS | `10.10.40.0/24` | 10.10.40.1 | 10.10.40.2 | 10.10.40.3 | HQ-DSW2 | SRV-DHCP (relay) |
| 50 | SERVIDORES | `10.10.50.0/24` | 10.10.50.1 | 10.10.50.2 | 10.10.50.3 | HQ-DSW1 | Estático |
| 99 | GESTION | `10.10.99.0/24` | 10.10.99.1 | 10.10.99.2 | 10.10.99.3 | HQ-DSW1 | Estático |

## VLANs · Sucursal Norte (BR1)

| VLAN | Nombre | Red | Gateway | DHCP |
|------|--------|-----|---------|------|
| 10 | ADMINISTRACION | `10.20.10.0/24` | 10.20.10.1 | Router local (.21 en adelante) |
| 20 | VENTAS | `10.20.20.0/24` | 10.20.20.1 | Router local (.21 en adelante) |
| 99 | GESTION | `10.20.99.0/24` | 10.20.99.1 | Estático |

## VLANs · Sucursal Sur (BR2)

| VLAN | Nombre | Red | Gateway | DHCP |
|------|--------|-----|---------|------|
| 10 | ADMINISTRACION | `10.30.10.0/24` | 10.30.10.1 | Router local (.21 en adelante) |
| 20 | VENTAS | `10.30.20.0/24` | 10.30.20.1 | Router local (.21 en adelante) |
| 99 | GESTION | `10.30.99.0/24` | 10.30.99.1 | Estático |

| VLAN | Nombre | Uso |
|------|--------|-----|
| 998 | NATIVA | VLAN nativa de todas las troncales (no lleva tráfico de usuarios) |
| 999 | SIN-USO | Puertos sin uso, apagados |

## Interfaces con IP

| Equipo | Interfaz | IP | Conectada a |
|--------|----------|----|-------------|
| HQ-EDGE1 | Loopback0 | `10.255.255.1/32` | Router ID |
| HQ-EDGE1 | GigabitEthernet0/0 | `10.255.1.1/30` | HQ-DSW1 Gi1/0/1 |
| HQ-EDGE1 | GigabitEthernet0/1 | `10.255.1.5/30` | HQ-DSW2 Gi1/0/1 |
| HQ-EDGE1 | GigabitEthernet0/2 | `198.51.100.2/30` | ISP1 Gi0/0 |
| HQ-EDGE1 | Tunnel1 | `172.16.1.1/30` | BR1-RTR (costo OSPF 10) |
| HQ-EDGE1 | Tunnel2 | `172.16.1.5/30` | BR2-RTR (costo OSPF 10) |
| HQ-EDGE2 | Loopback0 | `10.255.255.2/32` | Router ID |
| HQ-EDGE2 | GigabitEthernet0/0 | `10.255.1.9/30` | HQ-DSW1 Gi1/0/2 |
| HQ-EDGE2 | GigabitEthernet0/1 | `10.255.1.13/30` | HQ-DSW2 Gi1/0/2 |
| HQ-EDGE2 | GigabitEthernet0/2 | `198.51.100.10/30` | ISP2 Gi0/0 |
| HQ-EDGE2 | Tunnel1 | `172.16.2.1/30` | BR1-RTR (costo OSPF 100) |
| HQ-EDGE2 | Tunnel2 | `172.16.2.5/30` | BR2-RTR (costo OSPF 100) |
| HQ-DSW1 | Loopback0 | `10.255.255.3/32` | Router ID |
| HQ-DSW1 | GigabitEthernet1/0/1 | `10.255.1.2/30` | HQ-EDGE1 Gi0/0 |
| HQ-DSW1 | GigabitEthernet1/0/2 | `10.255.1.10/30` | HQ-EDGE2 Gi0/0 |
| HQ-DSW2 | Loopback0 | `10.255.255.4/32` | Router ID |
| HQ-DSW2 | GigabitEthernet1/0/1 | `10.255.1.6/30` | HQ-EDGE1 Gi0/1 |
| HQ-DSW2 | GigabitEthernet1/0/2 | `10.255.1.14/30` | HQ-EDGE2 Gi0/1 |
| HQ-ASW1 | Vlan99 | `10.10.99.11` | Gestión |
| HQ-ASW2 | Vlan99 | `10.10.99.12` | Gestión |
| HQ-ASW3 | Vlan99 | `10.10.99.13` | Gestión |
| BR1-RTR | Loopback0 | `10.255.255.11/32` | Router ID |
| BR1-RTR | GigabitEthernet0/1 | `198.51.100.6/30` | ISP1 Gi0/1 |
| BR1-RTR | Tunnel1 | `172.16.1.2/30` | HQ-EDGE1 (costo OSPF 10) |
| BR1-RTR | Tunnel2 | `172.16.2.2/30` | HQ-EDGE2 (costo OSPF 100) |
| BR1-SW | Vlan99 | `10.20.99.11` | Gestión |
| BR2-RTR | Loopback0 | `10.255.255.12/32` | Router ID |
| BR2-RTR | GigabitEthernet0/1 | `198.51.100.14/30` | ISP2 Gi0/1 |
| BR2-RTR | Tunnel1 | `172.16.1.6/30` | HQ-EDGE1 (costo OSPF 10) |
| BR2-RTR | Tunnel2 | `172.16.2.6/30` | HQ-EDGE2 (costo OSPF 100) |
| BR2-SW | Vlan99 | `10.30.99.11` | Gestión |
| ISP1 | GigabitEthernet0/0 | `198.51.100.1/30` | HQ-EDGE1 Gi0/2 |
| ISP1 | GigabitEthernet0/1 | `198.51.100.5/30` | BR1-RTR Gi0/1 |
| ISP1 | GigabitEthernet0/2 | `192.0.2.1/24` | INTERNET-WEB Fa0 |
| ISP1 | Serial0/0/0 | `198.51.100.17/30` | ISP2 Se0/0/0 |
| ISP2 | GigabitEthernet0/0 | `198.51.100.9/30` | HQ-EDGE2 Gi0/2 |
| ISP2 | GigabitEthernet0/1 | `198.51.100.13/30` | BR2-RTR Gi0/1 |
| ISP2 | Serial0/0/0 | `198.51.100.18/30` | ISP1 Se0/0/0 |

## Equipos finales

| Equipo | Tipo | IP | Gateway | DNS | Servicios |
|--------|------|----|---------|-----|-----------|
| SRV-WEB | Servidor | 10.10.50.10/24 | 10.10.50.1 | 10.10.50.11 | HTTP, HTTPS |
| SRV-DNS | Servidor | 10.10.50.11/24 | 10.10.50.1 | 10.10.50.11 | DNS |
| SRV-AAA | Servidor | 10.10.50.12/24 | 10.10.50.1 | 10.10.50.11 | AAA (TACACS+) |
| SRV-LOG | Servidor | 10.10.50.13/24 | 10.10.50.1 | 10.10.50.11 | Syslog, NTP, TFTP |
| SRV-DHCP | Servidor | 10.10.50.14/24 | 10.10.50.1 | 10.10.50.11 | DHCP (pools de la sede) |
| INTERNET-WEB | Servidor | 192.0.2.10/24 | 192.0.2.1 | 192.0.2.10 | HTTP, DNS público |
| PC-ADM-HQ | PC | DHCP (VLAN 10) | DHCP | DHCP | - |
| PC-VEN-HQ | PC | DHCP (VLAN 20) | DHCP | DHCP | - |
| PC-TI-HQ | PC | DHCP (VLAN 30) | DHCP | DHCP | - |
| AP-INVITADOS | AccessPoint-PT | - (VLAN 40) | DHCP | DHCP | SSID NetCorp-Invitados, WPA2-PSK |
| LAPTOP-INV | Laptop (tarjeta Wi-Fi) | DHCP (VLAN 40) | DHCP | DHCP | - |
| PC-ADM-BR1 | PC | DHCP (VLAN 10) | DHCP | DHCP | - |
| PC-VEN-BR1 | PC | DHCP (VLAN 20) | DHCP | DHCP | - |
| PC-ADM-BR2 | PC | DHCP (VLAN 10) | DHCP | DHCP | - |
| PC-VEN-BR2 | PC | DHCP (VLAN 20) | DHCP | DHCP | - |

## NAT

| Router | Interna | Pública | Tipo |
|--------|---------|---------|------|
| HQ-EDGE1 | `10.10.0.0/16` | 198.51.100.2 | PAT (overload) |
| HQ-EDGE1 | 10.10.50.10 | 203.0.113.10 | Estática (SRV-WEB publicado) |
| HQ-EDGE2 | `10.10.0.0/16` | 198.51.100.10 | PAT (overload) |
| HQ-EDGE2 | 10.10.50.10 | 203.0.113.10 | Estática (SRV-WEB publicado) |
| BR1-RTR | `10.20.0.0/16` | 198.51.100.6 | PAT (overload) |
| BR2-RTR | `10.30.0.0/16` | 198.51.100.14 | PAT (overload) |
