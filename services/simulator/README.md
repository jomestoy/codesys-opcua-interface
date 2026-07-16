# Simulator service

Simulador offline para demostrar:

- 200 columnas;
- endpoint CODESYS primario/secundario;
- failover del primario;
- flujo gravimetrico calculado por regresion;
- PI lento simulado;
- buzon de comandos confirmado por CODESYS simulado.

Ejecutar:

```powershell
python -m codesys_opcua_interface.demo --columns 200 --ticks 30
```
