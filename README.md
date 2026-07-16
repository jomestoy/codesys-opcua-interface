# CODESYS OPC UA Interface

Interface segura para integrar una plataforma operacional de columnas con un runtime CODESYS usando OPC UA.

Este proyecto es una base independiente para publicar el perfil CODESYS/OPC UA, sus plantillas de nodos, validaciones offline y documentación de integración. No abre sesiones OPC UA reales ni escribe a PLC por defecto.

## Estado

- Modo actual: plantilla/offline.
- Escritura real: bloqueada.
- Seguridad recomendada: OPC UA `Basic256Sha256` + `SignAndEncrypt`.
- Producción: requiere certificados, símbolos CODESYS exportados, FAT/SAT y aprobación OT.

## Estructura

```text
codesys_opcua_interface/
  profile.py              Perfil, nodos y validaciones offline
config/
  codesys-profile.example.json
docs/
  ARCHITECTURE.md
  SECURITY.md
tests/
  test_profile.py
```

## Uso local

```powershell
python -m pip install -e .
python -m pytest -q
python -m codesys_opcua_interface.profile validate
python -m codesys_opcua_interface.profile export
```

## Variables

Copiar `.env.example` a `.env` si se integra con un runner propio:

```text
CODESYS_OPCUA_ENDPOINT=opc.tcp://<codesys-runtime>:4840
CODESYS_OPCUA_NAMESPACE=urn:<codesys-project>:columnas
CODESYS_OPCUA_SECURITY_POLICY=Basic256Sha256
CODESYS_OPCUA_SECURITY_MODE=SignAndEncrypt
REAL_IO_ENABLED=false
```

## Símbolos propuestos

Las rutas son plantillas; no son mapas finales:

```text
ns=<validado>;s=GVL_Columns.C{column:03}.InputWeightKg
ns=<validado>;s=GVL_Columns.C{column:03}.OutputWeightKg
ns=<validado>;s=GVL_Columns.C{column:03}.TemperaturePv
ns=<validado>;s=GVL_Columns.C{column:03}.FlowSetpointLph
ns=<validado>;s=GVL_Columns.C{column:03}.PumpOutputPct
ns=<validado>;s=GVL_Columns.C{column:03}.Command
ns=<validado>;s=GVL_System.Heartbeat
```

## Próximo paso para hardware real

Implementar el cliente OPC UA real en el gateway, no en la interfaz web. El navegador nunca debe conectarse directamente al PLC.
