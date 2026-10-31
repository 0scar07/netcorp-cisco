# 6. Solución de problemas

Los problemas que más aparecen al montar esta red en Packet Tracer, con la causa y el arreglo.

## Al montar

| Síntoma | Causa | Arreglo |
|---------|-------|---------|
| El 3650 no enciende ni muestra CLI | No tiene fuente de poder | Pestaña Physical → agrega **AC-POWER-SUPPLY** |
| No aparecen los puertos `Serial0/0/0` | Falta el módulo | Apaga el router, agrega **HWIC-2T** y enciéndelo |
| `crypto isakmp policy` da `Invalid input` | La licencia securityk9 no está activa | [Paso 4 de la construcción](03-construccion.md#paso-4--activar-la-licencia-de-seguridad) y `reload` |
| `line vty 5 15` da error | Ese modelo solo tiene 5 líneas VTY | Ignóralo: las líneas 0-4 ya quedan configuradas |
| `crypto key generate rsa ... modulus 2048` no se acepta | Versión antigua de Packet Tracer | Usa `crypto key generate rsa general-keys modulus 1024` |
| `switchport trunk encapsulation dot1q` da error en el 3650 | Algunas versiones solo admiten 802.1Q y no aceptan el comando | Ignóralo: la troncal queda en 802.1Q igual |
| El CLI se atasca al pegar | Archivo largo | Pega por bloques separados por `!` |

## Capa 2

| Síntoma | Causa | Arreglo |
|---------|-------|---------|
| `Po1` aparece como `(SD)` | Los puertos miembros tienen configuraciones distintas | `show etherchannel summary` y `show run interface Gi1/0/23`; las dos puntas deben tener la misma troncal |
| Un PC no recibe IP en la sede | El relay no llega o falta el pool | `show run interface vlan 20` (debe tener `ip helper-address`) y revisa los pools de SRV-DHCP |
| Recibe IP del pool equivocado | El pool del servidor tiene mal la red de inicio | El **Start IP** de cada pool debe estar dentro de la red de su VLAN |
| Nadie recibe IP desde que activé DHCP snooping | El switch añade la opción 82 y el relay la descarta | `no ip dhcp snooping information option` (ya está en las configs) |
| Un puerto de usuario no pasa tráfico | Port-security en `restrict` descarta MACs nuevas | `show port-security interface Fa0/x`; para limpiar: `clear port-security sticky interface Fa0/x` |
| Puerto en `err-disabled` | BPDU Guard detectó un switch | Quita el switch y haz `shutdown` / `no shutdown` en el puerto |

## Enrutamiento

| Síntoma | Causa | Arreglo |
|---------|-------|---------|
| OSPF no forma vecinos en un enlace | Clave MD5 distinta o falta `message-digest-key` en un lado | `show ip ospf interface Gi0/0`: debe decir `Message digest authentication enabled` |
| Vecino OSPF en `INIT` por el túnel | El IPsec no está levantado y el GRE no pasa | Revisa `show crypto isakmp sa` antes que OSPF |
| Vecinos OSPF por el túnel se caen cada 20 s | Hellos y dead distintos en las dos puntas | Ambos lados deben tener `hello-interval 5` y `dead-interval 20` |
| HQ-DSW1 no tiene ruta por defecto | HQ-EDGE1 no tiene su estática a ISP1 o su WAN está caída | `show ip route static` en HQ-EDGE1 |
| BGP en `Idle` o `Active` | IP o AS del vecino mal escritos | `show ip bgp summary` y compara con el inventario |
| Internet no funciona pero el ping a la IP pública del ISP sí | Falta `ip nat inside` u `outside` en alguna interfaz | `show ip nat statistics` |

## VPN

| Síntoma | Causa | Arreglo |
|---------|-------|---------|
| `show crypto isakmp sa` vacío | No hay tráfico interesante todavía | Haz un ping entre sedes: el GRE de OSPF también lo levanta |
| Fase 1 en `MM_NO_STATE` | Clave precompartida distinta o política IKE distinta | Revisa `crypto isakmp key` y la `policy 10` en las dos puntas |
| Fase 1 arriba pero sin paquetes cifrados | La ACL de la crypto map no coincide con el GRE | Las dos puntas deben tener la ACL en espejo (`permit gre host A host B` y `permit gre host B host A`) |
| El túnel está `up/up` pero no pasa nada | Recursión de ruta: el destino del túnel se aprende por el propio túnel | Las IP públicas nunca deben entrar en OSPF; solo la ruta estática por defecto las alcanza |
