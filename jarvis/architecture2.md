"""
JARVIS v2 - Estructura Optimizada para Escalabilidad
=====================================================

Principios:
- Sin nombres duplicados
- Separación clara de responsabilidades
- Fácil onboarding para nuevos devs
- Hot-reload friendly
- Testeable

/jarvis/
│
├── core/                               # Motor central del sistema
│   ├── engine.py                       # Orquestador principal (antes core.py)
│   ├── config.py                       # Config loader con hot-reload
│   ├── events.py                       # Event bus (pub/sub)
│   ├── state.py                        # Estado global del sistema
│   └── lifecycle.py                    # Boot/shutdown hooks
│
├── brain/                              # Procesamiento inteligente (JAR)
│   ├── nlu/                            # Natural Language Understanding
│   │   ├── pipeline.py
│   │   ├── normalizer.py
│   │   ├── entities.py
│   │   └── parser.py
│   │
│   ├── llm/                            # Language Model Manager
│   │   ├── manager.py
│   │   ├── providers/                  # OpenAI, Ollama, etc
│   │   └── prompts/
│   │
│   ├── memory/                         # Sistema de memoria
│   │   ├── semantic.py                 # Embeddings & similarity
│   │   ├── context.py                  # Context window manager
│   │   └── storage.py                  # Persistencia
│   │
│   └── reasoning/                      # Lógica de decisión
│       ├── planner.py                  # Multi-step planning
│       ├── agent.py                    # Agentic behavior
│       └── rules.py                    # Rule-based fallbacks
│
├── skills/                             # Acciones ejecutables (VIS)
│   ├── registry.py                     # Skill dispatcher & loader
│   ├── base.py                         # BaseSkill class
│   │
│   ├── system/                         # OS-level operations
│   │   ├── apps.py                     # Open/close apps
│   │   ├── files.py                    # File operations
│   │   ├── process.py                  # Process management
│   │   └── network.py                  # Network utils
│   │
│   ├── productivity/                   # Productivity skills
│   │   ├── notes.py
│   │   ├── reminders.py
│   │   ├── calendar.py
│   │   └── search.py
│   │
│   ├── automation/                     # Advanced automation
│   │   ├── workflows.py                # Multi-step workflows
│   │   ├── triggers.py                 # Event-based triggers
│   │   └── macros.py                   # Recorded macros
│   │
│   └── external/                       # API integrations
│       ├── weather.py
│       ├── web_search.py
│       └── email.py
│
├── io/                                 # Input/Output adapters
│   ├── cli/                            # Command-line interface
│   │   ├── prompt.py
│   │   └── formatter.py
│   │
│   ├── voice/                          # Voice I/O
│   │   ├── stt.py                      # Speech-to-text
│   │   ├── tts.py                      # Text-to-speech
│   │   ├── wakeword.py                 # Wake word detection
│   │   └── vad.py                      # Voice activity detection
│   │
│   └── api/                            # REST/WebSocket API
│       ├── server.py                   # FastAPI/Express server
│       ├── routes.py                   # Endpoints
│       └── websocket.py                # Real-time communication
│
├── data/                               # Data management
│   ├── collector.py                    # Telemetry & analytics
│   ├── storage.py                      # SQLite/JSON persistence
│   ├── models.py                       # Data models
│   └── privacy.py                      # Privacy controls & export
│
├── monitoring/                         # Observability
│   ├── logger.py                       # Structured logging
│   ├── metrics.py                      # Performance metrics
│   ├── alerts.py                       # Alert system
│   └── debugger.py                     # Debug utilities
│
├── scheduler/                          # Task scheduling
│   ├── cron.py                         # Cron-like scheduler
│   ├── queue.py                        # Task queue
│   └── worker.py                       # Background workers
│
├── plugins/                            # Extensibility
│   ├── loader.py                       # Plugin loader
│   ├── registry.py                     # Plugin registry
│   └── installed/                      # User-installed plugins
│       └── .gitkeep
│
├── webapp/                             # MERN Dashboard
│   ├── backend/                        # Node.js + Express
│   │   ├── server.js
│   │   ├── routes/
│   │   ├── controllers/
│   │   └── middleware/
│   │
│   └── frontend/                       # React
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── hooks/
│       │   └── utils/
│       ├── public/
│       └── package.json
│
├── tests/                              # Testing suite
│   ├── unit/                           # Unit tests
│   ├── integration/                    # Integration tests
│   └── e2e/                            # End-to-end tests
│
├── docs/                               # Documentation
│   ├── architecture.md
│   ├── contributing.md
│   ├── skills.md                       # How to create skills
│   └── api.md                          # API documentation
│
├── scripts/                            # Utility scripts
│   ├── install.sh
│   ├── dev.sh
│   └── backup.py
│
├── main.py                             # Entry point
├── config.json                         # Configuration
├── requirements.txt                    # Python deps
├── package.json                        # Node deps (webapp)
├── .env.example                        # Environment variables
└── README.md


KEY IMPROVEMENTS vs v1:
========================

1. NO DUPLICATES:
   - "system/" eliminado (confuso con OS)
   - "actions/" renombrado a "skills/" (más claro)
   - "storage/" movido dentro de "data/"

2. CLEAR SEPARATION:
   - core/ = Motor
   - brain/ = Inteligencia
   - skills/ = Acciones
   - io/ = Interfaces
   - monitoring/ = Observabilidad

3. SCALABILITY:
   - webapp/ separado con su propio stack
   - plugins/ para extensiones
   - scheduler/ independiente
   - data/ con privacy by design

4. DEVELOPER FRIENDLY:
   - docs/ con guías claras
   - tests/ organizados por tipo
   - scripts/ para automatización

5. PRODUCTION READY:
   - monitoring/ completo
   - .env para secrets
   - logging estructurado
"""