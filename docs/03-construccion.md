# 3. Construcción en Packet Tracer

Guía paso a paso para montar la red desde cero en **Packet Tracer 8.2** o posterior.

> Packet Tracer guarda la topología en un archivo binario (`.pkt`) que no se puede generar desde código. Los equipos y los cables se ponen a mano siguiendo esta guía; las configuraciones sí salen listas de `configs/`.

## Paso 1 · Colocar los equipos

| Equipo | Modelo | Dónde está en Packet Tracer |
|--------|--------|------------------------------|
| HQ-EDGE1, HQ-EDGE2, BR1-RTR, BR2-RTR, ISP1, ISP2 | 2911 | Network Devices → Routers |
| HQ-DSW1, HQ-DSW2 | 3650-24PS | Network Devices → Switches |
| HQ-ASW1, HQ-ASW2, HQ-ASW3, BR1-SW, BR2-SW | 2960-24TT | Network Devices → Switches |
| SRV-WEB, SRV-DNS, SRV-AAA, SRV-LOG, SRV-DHCP, INTERNET-WEB | Server-PT | End Devices |
| PC-ADM-HQ, PC-VEN-HQ, PC-TI-HQ, PC-ADM-BR1, PC-VEN-BR1, PC-ADM-BR2, PC-VEN-BR2 | PC-PT | End Devices |
| LAPTOP-INV | Laptop-PT | End Devices |
| AP-INVITADOS | AccessPoint-PT | Network Devices → Wireless Devices |

Cambia el **Display Name** de cada equipo (pestaña Config) para que coincida con la tabla. Las configuraciones ponen el `hostname`, pero el nombre visible en el mapa se cambia a mano.

## Paso 2 · Agregar módulos

| Equipo | Qué hacer |
|--------|-----------|
| HQ-DSW1, HQ-DSW2 | Pestaña **Physical**: arrastra **AC-POWER-SUPPLY** a la ranura de la fuente. Sin fuente, el 3650 no enciende. |
| ISP1, ISP2 | Pestaña **Physical**: apaga el router, arrastra **HWIC-2T** a la primera ranura y vuelve a encenderlo. Da los puertos `Serial0/0/0` y `Serial0/0/1`. |
| LAPTOP-INV | Apágala, quita el módulo Ethernet, pon **WPC300N** (Wi-Fi) y enciéndela. |

## Paso 3 · Cablear

Sigue la tabla de [generado/cableado.md](generado/cableado.md) fila por fila. Tiene los 33 cables con el puerto exacto de cada lado.

- **Cobre directo** entre equipos de distinto tipo (router-switch, switch-PC).
- **Cobre cruzado** entre switches del mismo tipo (el EtherChannel entre HQ-DSW1 y HQ-DSW2).
- **Serial DCE** entre ISP1 e ISP2: empieza el cable en **ISP1**, que es el lado que da el reloj (`clock rate 64000`).

Si conectas un puerto distinto, la descripción de la interfaz no coincidirá. Lo correcto es cambiar el `enlaces` del inventario y volver a generar.

## Paso 4 · Activar la licencia de seguridad

Los comandos de IPsec (`crypto isakmp`, `crypto map`) solo existen con la licencia **securityk9**. Actívala en **HQ-EDGE1, HQ-EDGE2, BR1-RTR y BR2-RTR**:

```
enable
configure terminal
license boot module c2900 technology-package securityk9
yes
end
write memory
reload
```

Después del reinicio, comprueba con `show version` que `securityk9` aparece como **Permanent** o **Evaluation**.

## Paso 5 · Configurar los servidores

Los servidores se configuran desde su interfaz gráfica. Primero la IP (pestaña **Desktop → IP Configuration**), con los datos de [generado/direccionamiento.md](generado/direccionamiento.md#equipos-finales). Luego los servicios (pestaña **Services**). Apaga en cada servidor los servicios que no le tocan.

### SRV-DNS (10.10.50.11)

**DNS → On**, con estos registros A:

| Nombre | Dirección |
|--------|-----------|
| `www.netcorp.local` | 10.10.50.10 |
| `aaa.netcorp.local` | 10.10.50.12 |
| `log.netcorp.local` | 10.10.50.13 |
| `www.internet.test` | 192.0.2.10 |

### SRV-DHCP (10.10.50.14)

**DHCP → On**. Crea un pool por cada VLAN de la sede (el `serverPool` que trae por defecto puede quedarse, porque nadie en la VLAN 50 pide DHCP):

| Pool | Default Gateway | DNS Server | Start IP | Subnet Mask | Max Users |
|------|-----------------|------------|----------|-------------|-----------|
| ADMINISTRACION | 10.10.10.1 | 10.10.50.11 | 10.10.10.51 | 255.255.255.0 | 150 |
| VENTAS | 10.10.20.1 | 10.10.50.11 | 10.10.20.51 | 255.255.255.0 | 150 |
| TI | 10.10.30.1 | 10.10.50.11 | 10.10.30.51 | 255.255.255.0 | 150 |
| INVITADOS | 10.10.40.1 | 10.10.50.11 | 10.10.40.51 | 255.255.255.0 | 150 |

Los switches de distribución reenvían las solicitudes con `ip helper-address`, y el servidor elige el pool según la red de la SVI que hizo el relay.

### SRV-AAA (10.10.50.12)

**AAA → On**.

Agrega un usuario: `netadmin` con la clave `clave_usuario` del inventario.

Agrega un cliente por cada IP desde la que un equipo puede hablar con el servidor. Todos son de tipo **Tacacs** y usan como **Secret** el valor `tacacs` del inventario:

| Client Name | Client IP | Por qué esa IP |
|-------------|-----------|----------------|
| HQ-EDGE1-A | 10.255.1.1 | Sale por Gi0/0 |
| HQ-EDGE1-B | 10.255.1.5 | Sale por Gi0/1 (OSPF reparte entre las dos) |
| HQ-EDGE2-A | 10.255.1.9 | Sale por Gi0/0 |
| HQ-EDGE2-B | 10.255.1.13 | Sale por Gi0/1 |
| HQ-DSW1 | 10.10.50.2 | Tiene una SVI en la VLAN de servidores |
| HQ-DSW2 | 10.10.50.3 | Igual |
| HQ-ASW1 | 10.10.99.11 | IP de gestión |
| HQ-ASW2 | 10.10.99.12 | IP de gestión |
| HQ-ASW3 | 10.10.99.13 | IP de gestión |
| BR1-RTR-P | 172.16.1.2 | Túnel principal |
| BR1-RTR-R | 172.16.2.2 | Túnel de respaldo |
| BR2-RTR-P | 172.16.1.6 | Túnel principal |
| BR2-RTR-R | 172.16.2.6 | Túnel de respaldo |
| BR1-SW | 10.20.99.11 | IP de gestión |
| BR2-SW | 10.30.99.11 | IP de gestión |

Si el servidor no responde, los equipos dejan entrar con el usuario local (`aaa authentication login default group tacacs+ local`).

### SRV-LOG (10.10.50.13)

**SYSLOG → On**, **NTP → On** y **TFTP → On**.

### SRV-WEB (10.10.50.10)

**HTTP → On** y **HTTPS → On**. Edita `index.html` con algo que identifique a NetCorp, para reconocerlo en las pruebas.

### INTERNET-WEB (192.0.2.10)

**HTTP → On** y **DNS → On**, con estos registros:

| Nombre | Dirección |
|--------|-----------|
| `www.internet.test` | 192.0.2.10 |
| `www.netcorp.test` | 203.0.113.10 |

## Paso 6 · Pegar las configuraciones

Abre cada equipo, ve a la pestaña **CLI**, responde `no` al diálogo inicial, escribe `enable` y pega el archivo completo de `configs/`. El orden importa poco, pero este evita esperar a vecinos que todavía no existen:

1. `ISP1.txt`, `ISP2.txt`
2. `HQ-EDGE1.txt`, `HQ-EDGE2.txt`
3. `HQ-DSW1.txt`, `HQ-DSW2.txt`
4. `HQ-ASW1.txt`, `HQ-ASW2.txt`, `HQ-ASW3.txt`
5. `BR1-RTR.txt`, `BR1-SW.txt`, `BR2-RTR.txt`, `BR2-SW.txt`

Cada archivo termina con `write memory`, así que la configuración queda guardada.

> Un consejo: pega por bloques (separados por `!`) si el CLI de Packet Tracer se atasca con archivos largos. Los switches 3650 tardan un poco en generar la clave RSA de 2048 bits.

## Paso 7 · Equipos finales

- **PCs y laptop**: Desktop → IP Configuration → **DHCP**. Deben recibir IP del pool de su VLAN.
- **AP-INVITADOS**: pestaña Config → Port 1: SSID `NetCorp-Invitados`, autenticación **WPA2-PSK**, clave `Invitad0s2026`.
- **LAPTOP-INV**: Desktop → PC Wireless → conectar a `NetCorp-Invitados` con esa clave.

## Paso 8 · Guardar

Guarda la topología como `topologia/NetCorp.pkt` y súbela al repositorio. Luego sigue el [plan de pruebas](05-pruebas.md) y guarda las capturas en `evidencias/`.
