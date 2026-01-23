# Jarvis AI - Modo Daemon y Auto-Start

## Modo Daemon

Jarvis ahora soporta ejecución en modo daemon (background) sin mostrar consola.

### Uso Básico
```bash
# Modo normal (con consola)
python main.py

# Modo daemon (background, sin consola)
python main.py --daemon
```

### Logging en Modo Daemon
Cuando se ejecuta en modo daemon, todos los logs se guardan en:
`Desktop/JarvisData/logs/jarvis_daemon_YYYYMMDD.log`

## Auto-Start con Windows

### Configuración Automática
Ejecuta el script de setup para configurar auto-inicio:

```bash
# Desde el directorio raíz del proyecto
setup_jarvis_task.bat
```

Este script crea una tarea programada que ejecuta Jarvis al iniciar sesión en Windows.

### Inicio Manual
Para iniciar Jarvis manualmente en background:

```bash
# Desde el directorio raíz del proyecto
start_jarvis_daemon.bat
```

### Desactivar Auto-Start
Para remover la tarea programada:

```bash
schtasks /delete /tn "Jarvis AI Auto-Start" /f
```

## Notas Técnicas

- El modo daemon usa `pythonw.exe` para evitar mostrar la consola de Windows
- Los logs se redirigen automáticamente a archivo en modo daemon
- La tarea programada se ejecuta con privilegios altos para acceso completo al sistema
- Jarvis se ejecuta en background y puede ser controlado vía voz o interfaz web (futuro)

## Troubleshooting

### La tarea no se crea
- Ejecuta `setup_jarvis_task.bat` como administrador
- Verifica que los archivos `.bat` estén en el directorio correcto

### Jarvis no inicia
- Revisa los logs en `Desktop/JarvisData/logs/`
- Asegúrate de que Python esté en el PATH del sistema

### Detener Jarvis en modo daemon
- Busca `pythonw.exe` en el Administrador de Tareas
- Finaliza el proceso para detener Jarvis