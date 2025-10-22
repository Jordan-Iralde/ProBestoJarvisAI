| Prioridad | Mejora                 | Impacto  | Detalle                                                                                                                                  |
| --------- | ---------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 1         | Input dinámico         | Muy alto | Recibir comandos desde CLI, GUI y voz (STT), no hardcodear strings.                                                                      |
| 2         | Dispatcher modular     | Muy alto | Registrar módulos y comandos dinámicamente (dict o clase). Ej: `"clima": clima.obtener_clima`. Así agregas comandos sin tocar `main.py`. |
| 3         | Memoria / contexto     | Muy alto | Guardar historial de comandos y respuestas en SQLite/cache → útil para Planner, Dev Assistant, aprendizaje.                              |
| 4         | NLP / parseo intención | Alto     | Integrar `intent_parser.py` para interpretar variaciones de comandos (“qué hora es”, “dime la hora”, etc).                               |
| 5         | Threaded TTS y logging | Medio    | Evitar bloqueos; cada respuesta de voz en thread separado.                                                                               |
| 6         | Manejo de errores      | Medio    | Comandos desconocidos → sugerencias, fallback a “no entendí”.                                                                            |
| 7         | Integración futura VIS | Medio    | Cada comando puede generar un plan de acción para VIS (automatización).                                                                  |
