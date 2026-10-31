# Topología

[`NetCorp.pkt`](NetCorp.pkt) es la red montada en **Packet Tracer 9.0**: los 28 equipos, los 33 cables de [docs/generado/cableado.md](../docs/generado/cableado.md), los servidores configurados y las configuraciones de `configs/` ya pegadas y guardadas.

Al abrirlo, sigue los pasos de [Al abrir `topologia/NetCorp.pkt`](../docs/06-solucion-de-problemas.md#al-abrir-topologianetcorppkt): los routers con VPN necesitan un `copy startup-config running-config` porque Packet Tracer descarta los comandos `crypto` al arrancar.

Para montarla desde cero sigue [docs/03-construccion.md](../docs/03-construccion.md).
