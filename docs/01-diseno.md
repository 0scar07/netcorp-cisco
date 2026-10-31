# 1. Diseño y decisiones

## Escenario

NetCorp tiene una **sede central** con cuatro departamentos y una granja de servidores, y dos **sucursales** pequeñas. La empresa pidió:

| # | Requisito | Cómo se cumple |
|---|-----------|----------------|
| R1 | Ningún fallo de un solo equipo de la sede deja a los usuarios sin red | Dos switches de distribución con HSRP, troncales a ambos desde cada acceso y dos routers de borde |
| R2 | Internet no se cae si falla un proveedor | Dos ISP con eBGP y ruta por defecto principal y de respaldo |
| R3 | El tráfico entre sedes viaja cifrado | Túneles GRE sobre IPsec con AES-256 |
| R4 | Las sucursales siguen conectadas a la sede si cae el borde principal | Cada sucursal tiene un túnel principal (HQ-EDGE1) y uno de respaldo (HQ-EDGE2) |
| R5 | Los invitados tienen Internet pero no ven la red interna | VLAN propia con ACL que solo deja pasar DHCP, DNS e Internet |
| R6 | Los servidores solo exponen los servicios que dan | ACL de salida en la SVI de la VLAN 50 |
| R7 | Solo TI administra los equipos, con registro de quién entra | SSH v2 limitado a las redes de TI y gestión, AAA con TACACS+ y Syslog central |
| R8 | La red se puede crecer sin inconsistencias | Inventario único, configuraciones generadas y pruebas automáticas |

## Arquitectura

### Sede central: núcleo colapsado

Con siete switches no hace falta una capa de núcleo separada: **HQ-DSW1** y **HQ-DSW2** hacen de núcleo y distribución a la vez. Es el diseño que Cisco recomienda para campus de este tamaño, porque ahorra equipos sin perder redundancia.

- Cada switch de acceso sube con una troncal a cada switch de distribución. STP bloquea una de las dos y la abre en cuanto la otra falla.
- Los switches de distribución están unidos por un **EtherChannel LACP** de dos enlaces, para que el tráfico entre ellos no dependa de un solo cable.
- Las SVIs de cada VLAN viven en los dos switches con **HSRPv2**. El gateway de los usuarios siempre es la `.1` virtual.

### Balanceo de HSRP alineado con STP

Las VLANs se reparten entre los dos switches de distribución:

| Switch | HSRP activo y raíz de STP | En espera y raíz secundaria |
|--------|---------------------------|-----------------------------|
| HQ-DSW1 | 10, 30, 50, 99 | 20, 40 |
| HQ-DSW2 | 20, 40 | 10, 30, 50, 99 |

Si la raíz de STP de una VLAN estuviera en un switch y el HSRP activo en el otro, el tráfico tendría que cruzar el EtherChannel en cada paquete. Por eso las dos cosas se configuran juntas, y hay una prueba automática que lo comprueba.

### Borde: dos routers y dos proveedores

- **HQ-EDGE1** sale por ISP1 e inyecta la ruta por defecto en OSPF con métrica 10.
- **HQ-EDGE2** sale por ISP2 e inyecta la ruta por defecto con métrica 50.

Los switches de distribución prefieren la de menor métrica. Si HQ-EDGE1 o su enlace con ISP1 caen, su ruta estática desaparece, deja de anunciar la ruta por defecto y OSPF pasa todo a HQ-EDGE2 sin intervención manual.

Los dos routers anuncian por **eBGP** el bloque público `203.0.113.0/24` (AS 65100) y publican `SRV-WEB` con NAT estática en `203.0.113.10`, así el servidor sigue accesible desde Internet por cualquiera de los dos proveedores.

### OSPF multiárea

| Área | Qué contiene | ABR |
|------|--------------|-----|
| 0 | Sede central, enlaces de borde, túneles y loopbacks | — |
| 1 | LAN de la Sucursal Norte (`10.20.0.0/16`) | BR1-RTR |
| 2 | LAN de la Sucursal Sur (`10.30.0.0/16`) | BR2-RTR |

Cada router de sucursal es ABR y resume su área en una sola ruta `/16`. Así la sede recibe dos rutas en lugar de seis, y un cambio dentro de una sucursal no provoca recálculos SPF en el resto de la red.

Además, todas las interfaces del área 0 usan **autenticación MD5** y, en los switches de distribución, `passive-interface default`: solo se forman adyacencias donde deben formarse.

### VPN: por qué GRE sobre IPsec

IPsec por sí solo (con crypto map) no transporta multicast, y OSPF usa multicast para sus hellos. La solución clásica es:

1. Un **túnel GRE** entre las IP públicas lleva OSPF y el tráfico de usuarios como si fuera un enlace directo.
2. Una **crypto map** cifra todo el GRE entre esas mismas IP públicas.

La topología es en estrella con **dos hubs**: cada sucursal tiene un túnel a HQ-EDGE1 con costo OSPF 10 y otro a HQ-EDGE2 con costo 100. Con hellos cada 5 s y tiempo muerto de 20 s, si el túnel principal cae, OSPF cambia al respaldo en unos 20 segundos.

Las sucursales salen a Internet **directamente** por su proveedor (con PAT). Solo el tráfico hacia la sede entra en la VPN, lo que evita mandar toda la navegación por la sede.

## Qué pasa cuando algo falla

| Falla | Reacción de la red | Tiempo aproximado |
|-------|--------------------|-------------------|
| Cae un enlace del EtherChannel | LACP sigue con el otro miembro | Inmediato |
| Cae la troncal HQ-ASW1 ↔ HQ-DSW1 | RSTP habilita la troncal a HQ-DSW2 | 1-3 s |
| Se apaga HQ-DSW1 | HQ-DSW2 asume todas las IP virtuales de HSRP y RSTP reconverge | ~10 s (tiempo de espera de HSRP) |
| Se apaga HQ-EDGE1 | La ruta por defecto pasa a HQ-EDGE2 y las sucursales usan los túneles de respaldo | ~20-40 s (OSPF) |
| Cae el enlace HQ-EDGE1 ↔ ISP1 | Igual que el anterior: Internet por ISP2 y túneles por HQ-EDGE2 | ~20 s |
| Cae ISP1 por completo | La sede sigue por ISP2. **La Sucursal Norte queda aislada**, porque solo tiene ISP1 | — |

La última fila es una limitación conocida: cada sucursal tiene un solo proveedor. En una red real se resolvería con un segundo enlace (otro ISP o LTE), y está en los próximos pasos del proyecto.

## Límites de Packet Tracer

Algunas cosas que se harían en una red real no se pueden simular bien en Packet Tracer y se dejaron fuera a propósito:

- **DMVPN** y túneles dinámicos entre sucursales: el soporte es parcial.
- **`standby track`** para que HSRP reaccione a la caída de un enlace de subida: no está disponible en todos los modelos.
- **QoS** completa: Packet Tracer acepta parte de los comandos pero no simula colas.
- **Automatización en vivo** con Netmiko o Ansible: Packet Tracer no expone SSH hacia fuera del simulador. Por eso la automatización de este proyecto genera y valida las configuraciones en lugar de aplicarlas sola.
