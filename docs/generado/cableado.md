# Cableado físico

> Generado por `scripts/generar.py` desde `inventario/red.yml`. No editar a mano.

Conecta cada fila en Packet Tracer con el cable indicado. Las descripciones de las interfaces en las configuraciones salen de esta misma tabla.

| # | Equipo A | Puerto A | Equipo B | Puerto B | Cable |
|---|----------|----------|----------|----------|-------|
| 1 | HQ-EDGE1 | GigabitEthernet0/0 | HQ-DSW1 | GigabitEthernet1/0/1 | Cobre directo |
| 2 | HQ-EDGE1 | GigabitEthernet0/1 | HQ-DSW2 | GigabitEthernet1/0/1 | Cobre directo |
| 3 | HQ-EDGE2 | GigabitEthernet0/0 | HQ-DSW1 | GigabitEthernet1/0/2 | Cobre directo |
| 4 | HQ-EDGE2 | GigabitEthernet0/1 | HQ-DSW2 | GigabitEthernet1/0/2 | Cobre directo |
| 5 | HQ-DSW1 | GigabitEthernet1/0/23 | HQ-DSW2 | GigabitEthernet1/0/23 | Cobre cruzado |
| 6 | HQ-DSW1 | GigabitEthernet1/0/24 | HQ-DSW2 | GigabitEthernet1/0/24 | Cobre cruzado |
| 7 | HQ-DSW1 | GigabitEthernet1/0/3 | HQ-ASW1 | GigabitEthernet0/1 | Cobre directo |
| 8 | HQ-DSW2 | GigabitEthernet1/0/3 | HQ-ASW1 | GigabitEthernet0/2 | Cobre directo |
| 9 | HQ-DSW1 | GigabitEthernet1/0/4 | HQ-ASW2 | GigabitEthernet0/1 | Cobre directo |
| 10 | HQ-DSW2 | GigabitEthernet1/0/4 | HQ-ASW2 | GigabitEthernet0/2 | Cobre directo |
| 11 | HQ-DSW1 | GigabitEthernet1/0/5 | HQ-ASW3 | GigabitEthernet0/1 | Cobre directo |
| 12 | HQ-DSW2 | GigabitEthernet1/0/5 | HQ-ASW3 | GigabitEthernet0/2 | Cobre directo |
| 13 | HQ-ASW1 | FastEthernet0/1 | PC-ADM-HQ | FastEthernet0 | Cobre directo |
| 14 | HQ-ASW1 | FastEthernet0/11 | PC-VEN-HQ | FastEthernet0 | Cobre directo |
| 15 | HQ-ASW2 | FastEthernet0/1 | PC-TI-HQ | FastEthernet0 | Cobre directo |
| 16 | HQ-ASW2 | FastEthernet0/11 | AP-INVITADOS | Port 0 | Cobre directo |
| 17 | HQ-ASW3 | FastEthernet0/1 | SRV-WEB | FastEthernet0 | Cobre directo |
| 18 | HQ-ASW3 | FastEthernet0/2 | SRV-DNS | FastEthernet0 | Cobre directo |
| 19 | HQ-ASW3 | FastEthernet0/3 | SRV-AAA | FastEthernet0 | Cobre directo |
| 20 | HQ-ASW3 | FastEthernet0/4 | SRV-LOG | FastEthernet0 | Cobre directo |
| 21 | HQ-ASW3 | FastEthernet0/5 | SRV-DHCP | FastEthernet0 | Cobre directo |
| 22 | HQ-EDGE1 | GigabitEthernet0/2 | ISP1 | GigabitEthernet0/0 | Cobre directo |
| 23 | HQ-EDGE2 | GigabitEthernet0/2 | ISP2 | GigabitEthernet0/0 | Cobre directo |
| 24 | BR1-RTR | GigabitEthernet0/1 | ISP1 | GigabitEthernet0/1 | Cobre directo |
| 25 | BR2-RTR | GigabitEthernet0/1 | ISP2 | GigabitEthernet0/1 | Cobre directo |
| 26 | ISP1 | Serial0/0/0 | ISP2 | Serial0/0/0 | Serial DCE (lado ISP1) |
| 27 | ISP1 | GigabitEthernet0/2 | INTERNET-WEB | FastEthernet0 | Cobre directo |
| 28 | BR1-RTR | GigabitEthernet0/0 | BR1-SW | GigabitEthernet0/1 | Cobre directo |
| 29 | BR1-SW | FastEthernet0/1 | PC-ADM-BR1 | FastEthernet0 | Cobre directo |
| 30 | BR1-SW | FastEthernet0/11 | PC-VEN-BR1 | FastEthernet0 | Cobre directo |
| 31 | BR2-RTR | GigabitEthernet0/0 | BR2-SW | GigabitEthernet0/1 | Cobre directo |
| 32 | BR2-SW | FastEthernet0/1 | PC-ADM-BR2 | FastEthernet0 | Cobre directo |
| 33 | BR2-SW | FastEthernet0/11 | PC-VEN-BR2 | FastEthernet0 | Cobre directo |

## Modelos

| Equipo | Rol | Modelo en Packet Tracer |
|--------|-----|-------------------------|
| HQ-EDGE1 | borde | Cisco 2911 (licencia securityk9) |
| HQ-EDGE2 | borde | Cisco 2911 (licencia securityk9) |
| HQ-DSW1 | distribucion | Cisco 3650-24PS (con fuente AC) |
| HQ-DSW2 | distribucion | Cisco 3650-24PS (con fuente AC) |
| HQ-ASW1 | acceso | Cisco 2960-24TT |
| HQ-ASW2 | acceso | Cisco 2960-24TT |
| HQ-ASW3 | acceso | Cisco 2960-24TT |
| BR1-RTR | sucursal | Cisco 2911 (licencia securityk9) |
| BR1-SW | acceso | Cisco 2960-24TT |
| BR2-RTR | sucursal | Cisco 2911 (licencia securityk9) |
| BR2-SW | acceso | Cisco 2960-24TT |
| ISP1 | isp | Cisco 2911 + HWIC-2T |
| ISP2 | isp | Cisco 2911 + HWIC-2T |
| SRV-WEB | equipo final | Servidor |
| SRV-DNS | equipo final | Servidor |
| SRV-AAA | equipo final | Servidor |
| SRV-LOG | equipo final | Servidor |
| SRV-DHCP | equipo final | Servidor |
| INTERNET-WEB | equipo final | Servidor |
| PC-ADM-HQ | equipo final | PC |
| PC-VEN-HQ | equipo final | PC |
| PC-TI-HQ | equipo final | PC |
| AP-INVITADOS | equipo final | AccessPoint-PT |
| LAPTOP-INV | equipo final | Laptop (tarjeta Wi-Fi) |
| PC-ADM-BR1 | equipo final | PC |
| PC-VEN-BR1 | equipo final | PC |
| PC-ADM-BR2 | equipo final | PC |
| PC-VEN-BR2 | equipo final | PC |
