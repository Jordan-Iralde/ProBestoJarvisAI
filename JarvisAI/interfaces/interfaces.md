| Carpeta | ¿Qué hace?                                                                                                             |
| ------- | ---------------------------------------------------------------------------------------------------------------------- |
| `api/`  | Expone tu IA como una API REST o WebSocket. Ideal para conectarte desde una app móvil, otro backend o cliente externo. | TODAVIA NO
| `cli/`  | Interfaz de línea de comandos (Command Line Interface). Perfecta para probar rápido con `python interface.py`.         |
| `gui/`  | Interfaz gráfica para PC (con Tkinter, PyQt, etc). Acá tenés ventanas, botones, cámara, micrófono, etc.                |



/gui/
├── app.py             # Lanza la interfaz
├── widgets.py         # Define componentes visuales reutilizables
├── controladores.py   # Define la lógica de interacción (ej: escuchar voz)
└── video_stream.py    # Cámara y procesamiento visual
