# PLCopen XML

Este directorio contiene `codesys-control.plcopen.xml`, generado desde las fuentes ST con:

```powershell
python scripts\generate_plcopen.py
```

No se incluye un binario `.project` porque no puede generarse ni validarse sin CODESYS Development System.

El XML actual es una exportacion preliminar de fuentes. Debe importarse, ajustar tipos/tareas si CODESYS lo requiere, compilarse y probarse contra un runtime real antes de considerarlo operativo.
