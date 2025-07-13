/jarvis/
│
├── core/                        # Núcleo lógico
│   ├── engine.py               # Manejador central del flujo de la IA
│   ├── dispatcher.py           # Enrutador de tareas por función
│   └── utils.py                # Funciones auxiliares generales
│
├── interfaces/                   
│   ├── cli/
│   │   └── interface.py
│   ├── gui/
│   │   ├── app.py
│   │   └── widgets.py
│
├── modules/                    # Módulos por función de la IA
│   ├── reconocimiento_voz/
│   │   ├── voz_a_texto.py
│   │   ├── audio_input.py
│   │   └── transcripcion.py
│   ├── voz_jarvis/
│   │   └── virtual_voice.py
│
├── docs/                   
│   ├── architecture.md
│   ├── usage.md
├── main.py                     # Punto de entrada del programa
└── requirements.txt            # Dependencias
