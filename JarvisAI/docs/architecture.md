/jarvis/
│
├── core/                        # Núcleo de control y lógica principal
│   ├── engine.py               # Motor principal que orquesta JAR y VIS
│   ├── dispatcher.py           # Enrutador de tareas/comandos a módulos
│   ├── config.py               # Configuración global, variables, rutas
│   └── utils.py                # Funciones utilitarias
│
├── jar/                        # JAR: Lenguaje natural (NLP)
│   ├── intent_parser.py       # Parseo de intención
│   ├── nlu_pipeline.py        # Pipeline de comprensión
│   ├── memory.py              # Contexto y memoria
│   ├── training/              # Datos y scripts de entrenamiento
│   │   ├── dataset.csv
│   │   └── trainer.py
│   └── models/                # Modelos entrenados y serializados
│       └── nlu_model.pkl
│
├── vis/                        # VIS: Automatización del sistema
│   ├── task_manager.py        # Planificación y ejecución de tareas
│   ├── os_hooks.py            # Ganchos al SO (registro, procesos, etc)
│   ├── app_control.py         # Control de ventanas, apps y entrada
│   └── tracker.py             # Trackeo del uso de PC/apps
│
├── interfaces/                 # Interfaz CLI y GUI
│   ├── cli/
│   │   └── interface.py
│   ├── gui/
│   │   ├── app.py
│   │   └── widgets.py
│
├── modules/                    # Módulos funcionales independientes
│   ├── voice_recognition/     # Reconocimiento de voz
│   │   ├── audio_input.py
│   │   ├── transcripcion.py
│   ├── virtual_voice/         # Voz sintética (Jarvis hablando)
│   │   └── virtual_voice.py
│   ├── web_search/            # Búsquedas inteligentes
│   │   └── google_module.py
│   └── telemetry/             # Recolección de datos y stats
│       └── collector.py
│
├── data/                       # Carpeta para logs, output, cache temporal
│   ├── logs/
│   └── cache/

├── tests/                      # Tests automatizados
│   └── test_engine.py
│
├── webapp/                     # Página de demostración para mostrar Jarvis
│   ├── public/
│   ├── pages/
│   └── api/
│
├── .gitignore
├── LICENSE (MIT)
├── README.md
├── CHANGELOG.md
├── requirements.txt
└── main.py                     # Punto de entrada principal
