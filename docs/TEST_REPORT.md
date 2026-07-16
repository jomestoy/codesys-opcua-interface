# Informe de pruebas

Fecha: 2026-07-15.

## codesys-opcua-interface

Comando:

```powershell
python -m pytest -q
```

Resultado:

```text
10 passed
```

Cobertura funcional validada:

- perfil seguro offline;
- rechazo de modo OPC UA inseguro;
- regresion lineal para flujo gravimetrico;
- congelacion del estimador por timestamp no monotonico;
- PI lento con rate limit y freeze;
- TTL e idempotencia de comandos;
- rechazo de setpoint fuera de rango;
- failover simulado activo/standby;
- NodeId con namespace resuelto.

## column-gateway

Comando:

```powershell
python -m pytest -q
```

Resultado:

```text
7 passed
```

Cobertura funcional validada:

- configuracion simulada valida;
- bloqueo de escritura real con `REAL_IO_ENABLED=false`;
- driver simulado lectura/escritura en memoria;
- buffer FIFO;
- servicio gateway con dispositivo simulado;
- parser de referencia LP7516.

## No validado en este ambiente

- CODESYS real;
- OPC UA real con certificados;
- hardware Modbus/RS232;
- systemd;
- paquetes Debian instalados;
- red dual NIC/nftables;
- Grafana/Node-RED ejecutandose.
