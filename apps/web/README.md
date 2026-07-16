# Web app

Aplicacion React + TypeScript + Vite + Material UI para la plataforma principal.

Estado Hito 4:

- login contra API;
- resumen ejecutivo;
- planta de 200 columnas por bloque;
- detalle de columna;
- solicitud de comandos por API (`start`, `pause`, `stop`, `set_flow`);
- recetas con crear/aprobar;
- recetas con crear, clonar, aprobar, rechazar, obsoletar, comparar y asignar;
- campanas con crear, programar, iniciar, pausar, finalizar, cancelar y exportar;
- alarmas con reglas configurables, evaluacion, reconocimiento y limpieza;
- usuarios con creacion y foto de perfil por URL;
- auditoria.

La regla de seguridad se mantiene: el frontend nunca escribe a dispositivos de campo; solo solicita comandos a la API. La API envia esas solicitudes al buzon OPC UA simulado/real para que CODESYS confirme.

## Ejecutar

```powershell
cd apps/web
npm install
npm run dev
```

Variables:

```text
VITE_API_URL=http://localhost:8000
```

En este ambiente local no se ejecuto `npm install` porque Node/npm no estaban en PATH y no hay `node_modules` versionado. La fuente queda preparada para instalar dependencias y compilar.
