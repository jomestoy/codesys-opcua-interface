# Arquitectura CODESYS OPC UA

## Responsabilidades

- CODESYS: lógica PLC, interlocks locales, publicación OPC UA y confirmaciones.
- Gateway/API: cliente OPC UA, validación, auditoría, autoridad de escritura y persistencia.
- Web: visualización y solicitud de acciones; nunca se conecta directo al PLC.

## Flujo

```text
Web -> API -> Gateway OPC UA client -> CODESYS OPC UA Server -> Hardware
```

El flujo medido se calcula por delta de peso de balanzas. El setpoint de flujo es una consigna independiente.

## Nodos

Los nodos en este repo son plantillas. Para producción se deben exportar símbolos desde CODESYS y aprobar:

- namespace;
- rutas simbólicas;
- tipos de dato;
- escalas y unidades;
- permisos de lectura/escritura;
- frecuencia de muestreo;
- confirmaciones de comando.
