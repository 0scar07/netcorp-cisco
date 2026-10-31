# 4. Seguridad

Los controles están organizados por **plano**, que es como se suele auditar un equipo de red: quién lo administra (gestión), cómo hablan los equipos entre sí (control) y qué tráfico de usuarios pasa (datos).

## Plano de gestión

| Control | Dónde | Comando clave |
|---------|-------|---------------|
| Solo SSH v2, sin Telnet | Todos los equipos de NetCorp | `ip ssh version 2`, `transport input ssh` |
| SSH solo desde TI y gestión | Todos | `access-class GESTION-SSH in` |
| Autenticación central con respaldo local | Todos | `aaa authentication login default group tacacs+ local` |
| Bloqueo por fuerza bruta | Todos | `login block-for 120 attempts 3 within 60` |
| Claves cifradas y con largo mínimo | Todos | `enable secret`, `service password-encryption`, `security passwords min-length 10` |
| Cierre de sesiones inactivas | Consola y VTY | `exec-timeout 10 0` |
| Aviso legal al conectarse | Todos | `banner motd` |
| SVI de la VLAN 1 apagada | Switches de acceso | `interface Vlan1` + `shutdown` |

## Plano de control

| Control | Para qué | Comando clave |
|---------|----------|---------------|
| Autenticación MD5 de OSPF | Que nadie meta rutas falsas en la red | `area 0 authentication message-digest` |
| `passive-interface default` | No mandar hellos de OSPF a las VLANs de usuarios | En los switches de distribución |
| Raíz de STP fija | Que un switch ajeno no se convierta en raíz | `spanning-tree vlan ... root primary` |
| BPDU Guard | Apagar un puerto de usuario si alguien conecta un switch | `spanning-tree bpduguard enable` |
| Troncales sin DTP | Evitar ataques de salto de VLAN (switch spoofing) | `switchport nonegotiate` |
| VLAN nativa sin uso | Evitar el doble etiquetado | `switchport trunk native vlan 998` |

## Plano de datos

| Control | Para qué | Dónde |
|---------|----------|-------|
| Port-security con MAC sticky | Limitar cuántos equipos se conectan por puerto | Puertos de acceso (1 MAC en servidores, 2 en usuarios, 15 en el AP) |
| DHCP snooping | Bloquear servidores DHCP falsos | Switches de acceso; solo las troncales son de confianza |
| ACL `INVITADOS` | Los invitados no llegan a ninguna red interna | Entrada de la SVI 40 |
| ACL `SERVIDORES` | Cada servidor solo recibe el tráfico de su servicio | Salida de la SVI 50 |
| Puertos sin uso apagados | Nadie conecta nada en un puerto libre | VLAN 999 + `shutdown` |
| VPN con AES-256 | El tráfico entre sedes no viaja en claro por Internet | Routers de borde y de sucursal |
| NAT | Las IP internas no se ven desde Internet | Routers de borde y de sucursal |

### Qué deja pasar la ACL `SERVIDORES`

| Origen | Destino | Servicio |
|--------|---------|----------|
| Cualquiera (incluido Internet, vía NAT) | SRV-WEB | HTTP 80, HTTPS 443 |
| Redes internas y túneles | SRV-DNS | DNS 53/udp |
| Redes internas y túneles | SRV-DHCP | DHCP 67/udp (relay) |
| Redes internas y túneles | SRV-AAA | TACACS+ 49/tcp |
| Redes internas y túneles | SRV-LOG | Syslog 514, NTP 123, TFTP 69 |
| Redes internas y túneles | Toda la VLAN | ping |
| TI y gestión | Toda la VLAN | Todo |
| Cualquier otro | — | Denegado |

## Visibilidad

- **Syslog** central en SRV-LOG con marcas de tiempo en milisegundos.
- **NTP** desde SRV-LOG, para que los registros de todos los equipos se puedan comparar.
- **SNMP** de solo lectura.

## Lo que falta y por qué

| Mejora | Motivo por el que no está |
|--------|---------------------------|
| SNMPv3 | Packet Tracer solo simula bien SNMPv2c |
| Dynamic ARP Inspection | Soporte limitado en el 2960 de Packet Tracer |
| 802.1X en los puertos de usuario | Necesita un RADIUS que valide equipos, fuera del alcance del laboratorio |
| ACL de entrada en las WAN | Pendiente: hay que permitir IKE, ESP, BGP y el tráfico de vuelta del NAT sin romper nada |
