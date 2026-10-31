# 5. Plan de pruebas

Cada prueba dice qué comando ejecutar, en qué equipo y qué resultado se espera. Guarda una captura de cada una en `evidencias/` con el ID de la prueba como nombre (por ejemplo `evidencias/L2-03.png`) y marca la casilla.

> **Última ejecución:** Packet Tracer 9.0, 31/10/2026. ✅ cumple · ⚠️ cumple en parte · ❌ no cumple. Cada marca enlaza a su captura. Las causas de ⚠️ y ❌ están en [Limitaciones de Packet Tracer](06-solucion-de-problemas.md#limitaciones-de-packet-tracer-90).

> En Packet Tracer el primer ping suele perder algún paquete mientras se resuelve ARP. Repítelo antes de dar una prueba por fallida.

## Capa 2

| ID | Prueba | Dónde | Comando | Resultado esperado | ✓ |
|----|--------|-------|---------|--------------------|---|
| L2-01 | VLANs creadas | HQ-ASW1 | `show vlan brief` | VLANs 10, 20, 30, 40, 50, 99, 998 y 999; Fa0/1-10 en la 10 y Fa0/11-20 en la 20 | [✅](../evidencias/L2-01.png) |
| L2-02 | Troncales | HQ-DSW1 | `show interfaces trunk` | Po1 y Gi1/0/3-5 en modo trunk, nativa 998, VLANs 10,20,30,40,50,99 | [✅](../evidencias/L2-02.png) |
| L2-03 | EtherChannel | HQ-DSW1 | `show etherchannel summary` | `Po1(SU)` con Gi1/0/23 y Gi1/0/24 en `(P)` | [✅](../evidencias/L2-03.png) |
| L2-04 | Raíz de STP | HQ-DSW1 | `show spanning-tree vlan 10` | `This bridge is the root` | [✅](../evidencias/L2-04.png) |
| L2-05 | Raíz de STP | HQ-DSW2 | `show spanning-tree vlan 20` | `This bridge is the root` | [✅](../evidencias/L2-05.png) |
| L2-06 | Puerto bloqueado | HQ-ASW1 | `show spanning-tree vlan 10` | Gi0/1 raíz (FWD), Gi0/2 alternativo (BLK) | [✅](../evidencias/L2-06.png) |
| L2-07 | Port-security | HQ-ASW1 | `show port-security` | Fa0/1-20 con máximo 2 y acción Restrict | [✅](../evidencias/L2-07.png) |
| L2-08 | DHCP snooping | HQ-ASW1 | `show ip dhcp snooping` | Activo en VLANs 10,20,30,40; Gi0/1 y Gi0/2 de confianza | [✅](../evidencias/L2-08.png) |

## HSRP y DHCP

| ID | Prueba | Dónde | Comando | Resultado esperado | ✓ |
|----|--------|-------|---------|--------------------|---|
| HA-01 | Estado de HSRP | HQ-DSW1 | `show standby brief` | Active en 10, 30, 50, 99; Standby en 20 y 40 | [✅](../evidencias/HA-01.png) |
| HA-02 | Estado de HSRP | HQ-DSW2 | `show standby brief` | Al revés que HQ-DSW1 | [✅](../evidencias/HA-02.png) |
| HA-03 | DHCP por relay | PC-VEN-HQ | IP Configuration → DHCP | IP `10.10.20.51` o siguiente, gateway `10.10.20.1`, DNS `10.10.50.11` | [✅](../evidencias/HA-03.png) |
| HA-04 | DHCP en sucursal | PC-ADM-BR1 | IP Configuration → DHCP | IP `10.20.10.21` o siguiente, gateway `10.20.10.1` | [✅](../evidencias/HA-04.png) |
| HA-05 | Wi-Fi de invitados | LAPTOP-INV | `ipconfig` | IP en `10.10.40.0/24` | [✅](../evidencias/HA-05.png) |

## Enrutamiento

| ID | Prueba | Dónde | Comando | Resultado esperado | ✓ |
|----|--------|-------|---------|--------------------|---|
| RT-01 | Vecinos OSPF | HQ-EDGE1 | `show ip ospf neighbor` | HQ-DSW1, HQ-DSW2, BR1-RTR y BR2-RTR en `FULL` | [✅](../evidencias/RT-01.png) |
| RT-02 | Vecinos OSPF | HQ-DSW1 | `show ip ospf neighbor` | HQ-EDGE1, HQ-EDGE2 y HQ-DSW2 (por la Vlan99) en `FULL` | [✅](../evidencias/RT-02.png) |
| RT-03 | Resumen de sucursales | HQ-DSW1 | `show ip route ospf` | `O IA 10.20.0.0/16` y `O IA 10.30.0.0/16`, sin las `/24` de las sucursales | [✅](../evidencias/RT-03.png) |
| RT-04 | Ruta por defecto | HQ-DSW1 | `show ip route 0.0.0.0` | `O*E2` con métrica 10, vía HQ-EDGE1 | [⚠️](../evidencias/RT-04.png) |
| RT-05 | Túnel principal | BR1-RTR | `show ip route 10.10.10.0` | Salida por `Tunnel1` | [⚠️](../evidencias/RT-05.png) |
| RT-06 | Vecinos BGP | HQ-EDGE1 | `show ip bgp summary` | ISP1 (198.51.100.1) establecido con prefijos recibidos | [✅](../evidencias/RT-06.png) |
| RT-07 | Anuncio del bloque público | ISP1 | `show ip bgp` | `203.0.113.0/24` con AS path `65100` | [✅](../evidencias/RT-07.png) |

## VPN

| ID | Prueba | Dónde | Comando | Resultado esperado | ✓ |
|----|--------|-------|---------|--------------------|---|
| VPN-01 | Fase 1 | HQ-EDGE1 | `show crypto isakmp sa` | Dos SA en `QM_IDLE` (BR1 y BR2) | [✅](../evidencias/VPN-01.png) |
| VPN-02 | Fase 2 cifrando | HQ-EDGE1 | `show crypto ipsec sa` | Los contadores `#pkts encaps` y `#pkts decaps` suben al hacer ping entre sedes | [✅](../evidencias/VPN-02.png) |
| VPN-03 | Sede ↔ sucursal | PC-ADM-BR1 | `ping 10.10.50.10` | Respuesta | [✅](../evidencias/VPN-03.png) |
| VPN-04 | Sucursal ↔ sucursal | PC-ADM-BR1 | `ping <IP de PC-ADM-BR2>` | Respuesta (pasando por la sede) | [✅](../evidencias/VPN-04.png) |
| VPN-05 | Camino | PC-ADM-BR1 | `tracert 10.10.50.10` | Pasa por `172.16.1.1` (HQ-EDGE1) | [✅](../evidencias/VPN-05.png) |

## Servicios y NAT

| ID | Prueba | Dónde | Comando | Resultado esperado | ✓ |
|----|--------|-------|---------|--------------------|---|
| SV-01 | DNS interno | PC-ADM-HQ | Web Browser → `www.netcorp.local` | Página de SRV-WEB | [✅](../evidencias/SV-01.png) |
| SV-02 | Internet desde la sede | PC-ADM-HQ | Web Browser → `www.internet.test` | Página de INTERNET-WEB | [❌](../evidencias/SV-02.png) |
| SV-03 | PAT | HQ-EDGE1 | `show ip nat translations` (después de SV-02) | Traducciones de `10.10.10.x` a `198.51.100.2` | [✅](../evidencias/SV-03.png) |
| SV-04 | Servidor publicado | INTERNET-WEB | Web Browser → `http://203.0.113.10` | Página de SRV-WEB (NAT estática) | [❌](../evidencias/SV-04.png) |
| SV-05 | Internet desde sucursal | PC-VEN-BR2 | Web Browser → `http://192.0.2.10` | Página de INTERNET-WEB, con PAT en BR2-RTR | [✅](../evidencias/SV-05.png) |
| SV-06 | Syslog | SRV-LOG | Services → SYSLOG | Mensajes de los equipos (por ejemplo, al apagar una interfaz) | [✅](../evidencias/SV-06.png) |
| SV-07 | NTP | HQ-DSW1 | `show ntp status` | `Clock is synchronized` con 10.10.50.13 | [✅](../evidencias/SV-07.png) |

## Seguridad

| ID | Prueba | Dónde | Comando | Resultado esperado | ✓ |
|----|--------|-------|---------|--------------------|---|
| SEC-01 | SSH desde TI | PC-TI-HQ | `ssh -l netadmin 10.10.99.2` | Entra (pide clave al AAA) | [✅](../evidencias/SEC-01.png) |
| SEC-02 | SSH desde Ventas | PC-VEN-HQ | `ssh -l netadmin 10.10.99.2` | Rechazado por `GESTION-SSH` | [✅](../evidencias/SEC-02.png) |
| SEC-03 | Telnet | PC-TI-HQ | `telnet 10.10.99.2` | Rechazado | [✅](../evidencias/SEC-03.png) |
| SEC-04 | Invitados aislados | LAPTOP-INV | `ping 10.10.10.1` y `ping 10.10.50.10` | Sin respuesta | [❌](../evidencias/SEC-04.png) |
| SEC-05 | Invitados con Internet | LAPTOP-INV | Web Browser → `www.internet.test` | Página de INTERNET-WEB | [❌](../evidencias/SEC-05.png) |
| SEC-06 | ACL de servidores | PC-VEN-HQ | Web Browser → `http://10.10.50.10` y luego `ftp 10.10.50.10` | La web abre; el FTP no conecta. En HQ-DSW2 (gateway activo de Ventas), `show access-lists SERVIDORES` suma coincidencias en `deny ip any any` | [⚠️](../evidencias/SEC-06-web.png) |
| SEC-07 | Puerto sin uso | HQ-ASW1 | `show interfaces status` | Fa0/21-24 en `disabled`, VLAN 999 | [✅](../evidencias/SEC-07.png) |
| SEC-08 | BPDU Guard | HQ-ASW1 | Conecta un switch extra a Fa0/5 | El puerto pasa a `err-disabled` | [✅](../evidencias/SEC-08.png) |
| SEC-09 | Bloqueo por intentos | PC-TI-HQ | 3 SSH con clave mala | `login block-for` deja el equipo en modo silencioso 120 s | [✅](../evidencias/SEC-09.png) |

## Pruebas de fallo

Haz un `ping -t` continuo desde el equipo indicado antes de provocar el fallo, y anota cuántos paquetes se pierden.

| ID | Fallo provocado | Ping continuo | Resultado esperado | ✓ |
|----|-----------------|---------------|--------------------|---|
| FO-01 | Desconecta un cable del Po1 | PC-ADM-HQ → PC-VEN-HQ | Sin pérdidas; `Po1` sigue `(SU)` con un miembro | [✅](../evidencias/FO-01.png) |
| FO-02 | Apaga Gi0/1 de HQ-ASW1 | PC-ADM-HQ → 10.10.50.10 | Se pierden 1-3 paquetes; Gi0/2 pasa a FWD | [✅](../evidencias/FO-02.png) |
| FO-03 | Apaga HQ-DSW1 | PC-ADM-HQ → 10.10.50.10 | Pérdida breve; `show standby brief` en HQ-DSW2 muestra todo Active | [✅](../evidencias/FO-03.png) |
| FO-04 | Vuelve a encender HQ-DSW1 | — | Recupera el rol Active en 10, 30, 50 y 99 (`preempt`) | [✅](../evidencias/FO-04.png) |
| FO-05 | `shutdown` en Gi0/2 de HQ-EDGE1 | PC-ADM-HQ → 192.0.2.10 | Pérdida de ~20 s; luego sale por HQ-EDGE2 (`show ip route 0.0.0.0` en HQ-DSW1 muestra métrica 50) | [✅](../evidencias/FO-05.png) |
| FO-06 | Mismo fallo que FO-05 | PC-ADM-BR1 → 10.10.50.10 | Pérdida de ~20 s; BR1-RTR pasa a `Tunnel2` | [✅](../evidencias/FO-06.png) |
| FO-07 | Mismo fallo que FO-05 | INTERNET-WEB → 203.0.113.10 | El servidor sigue publicado por ISP2 | [✅](../evidencias/FO-07.png) |
| FO-08 | `no shutdown` en Gi0/2 de HQ-EDGE1 | — | Vuelve todo al camino principal | [⚠️](../evidencias/FO-08.png) |

## Comandos de diagnóstico rápido

```
show ip interface brief
show running-config | section ospf
show ip ospf interface brief
show ip protocols
show ip route
show standby brief
show etherchannel summary
show spanning-tree summary
show crypto isakmp sa
show crypto ipsec sa
show ip nat translations
show ip bgp summary
show logging
```
