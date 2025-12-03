/jarvis/
│
├── system/                             # Orquestación real del sistema
│   ├── boot/                           # Secuencia de arranque
│   │   ├── loader.py                   # Carga módulos dinámicos
│   │   ├── initializer.py              # Configuración inicial
│   │   └── diagnostics.py              # Pruebas internas del sistema
│   │
│   ├── runtime/                        # Lo que vive mientras JARVIS corre
│   │   ├── events.py                   # Sistema de eventos interno (pub/sub)
│   │   ├── state.py                    # Estado vivo del sistema
│   │   ├── scheduler.py                # Tareas periódicas
│   │   └── watchdog.py                 # Monitoreo y autorecuperación
│   │
│   └── core.py                         # Orquestador principal (JARVIS Core)
│
├── brain/                              # Procesamiento inteligente
│   ├── nlu/                            # Lenguaje natural
│   │   ├── pipeline.py                 # Pipeline NLU
│   │   ├── intents.py                  # Detección de intención
│   │   ├── entities.py                 # Extracción de entidades
│   │   └── memory.py                   # Memoria semántica
│   │
│   ├── llm/                            # Lógica de modelos (si usás offline, acá)
│   │   ├── manager.py
│   │   └── models/
│   │
│   └── reasoning/                      # Razonamiento, planificación, contexto
│       ├── planner.py
│       ├── agent.py
│       └── context.py
│
├── actions/                            # Acciones y skills (VIS, OS, apps)
│   ├── base/                           # Clases base para acciones
│   │   └── action.py
│   │
│   ├── system/                         # Acciones del sistema operativo
│   │   ├── os_hooks.py
│   │   ├── file_ops.py
│   │   └── app_control.py
│   │
│   ├── skills/                         # Skills modulares
│   │   ├── weather.py
│   │   ├── notes.py
│   │   ├── reminders.py
│   │   └── web_search.py
│   │
│   └── automation/                     # Automatizaciones avanzadas
│       ├── triggers.py
│       └── rules_engine.py
│
├── io/                                 # Todo lo que entra y sale del sistema
│   ├── audio/
│   │   ├── loop.py                     # Captura continua
│   │   ├── vad.py                      # Voice activity detection
│   │   ├── wakeword.py                 # Hotword
│   │   └── stt.py                      # Transcripción
│   │
│   ├── speech/
│   │   └── tts.py                      # Voz sintética
│   │
│   ├── text/
│   │   ├── input_adapter.py
│   │   └── output_adapter.py
│   │
│   └── gui/                            # Interfaces visuales
│       ├── dashboard/
│       │   ├── api.py
│       │   └── views.py
│       └── cli/
│           └── cli.py
│
├── modules/                            # Extensiones externas (plugins)
│   ├── loader.py                       # Carga módulos externos
│   └── installed/                      # Cada módulo aislado
│       └── example_module/
│           └── module.py
│
├── storage/                            # Persistencia
│   ├── sqlite/                         # DB local
│   ├── cache/
│   └── logs/
│
├── tests/                              # Tests reales
│   ├── test_nlu.py
│   ├── test_skills.py
│   └── test_runtime.py
│
├── webapp/                             # Dashboard externo (React/Next)
│   └── ...
│
├── main.py                             # Punto de entrada
└── config.json                         # Config



JAR = /brain/ entero
Incluye:
nlu/
reasoning/
llm/
memory

Funciona como la “mente” del sistema.
Procesa → entiende → decide.

VIS = /actions/ entero
Incluye:
system/ (hooks, apps, SO)
skills/ (acciones específicas)
automation/ (reglas, triggers, planificaciones)

Esto es el “cuerpo” del sistema.
Ejecuta → controla → modifica el entorno.