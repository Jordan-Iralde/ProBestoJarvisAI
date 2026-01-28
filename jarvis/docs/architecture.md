# JarvisAI v0.0.4 - System Architecture

> Complete system design and module documentation

## 🏗️ System Overview

JarvisAI is built on a modular, event-driven architecture designed for scalability, learning, and autonomous operation.

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  Voice (STT/TTS) │ CLI │ Text Input │ Dashboard (Optional)  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                  Core Engine (JarvisCore)                   │
│  - Event Bus & Scheduling                                   │
│  - Skill Dispatcher                                         │
│  - Runtime State Management                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
┌──────▼────┐   ┌──────▼────┐   ┌──────▼────┐
│   Brain    │   │  Skills   │   │   Data    │
│  (NLU/LLM) │   │ (Actions) │   │ (Storage) │
└────────────┘   └────────────┘   └───────────┘
```

---

## 📁 Directory Structure

### **core/** - Core Lifecycle & Boot
Centralized core components managing system initialization and runtime.

```
core/
├── __init__.py                # Package exports
├── constants.py               # System constants, events, modes
├── modes.py                   # Operational modes (SAFE/PASSIVE/ACTIVE/ANALYSIS)
└── lifecycle/
    ├── __init__.py
    ├── boot/
    │   ├── __init__.py
    │   ├── initializer.py      # System initialization
    │   ├── diagnostics.py      # System diagnostics
    │   └── loader.py           # Module loader with error handling
    ├── runtime/
    │   ├── __init__.py
    │   ├── state.py            # RuntimeState class
    │   ├── events.py           # EventBus (pub/sub system)
    │   ├── scheduler.py        # Task scheduler
    │   ├── io.py               # I/O management
    │   └── watchdog.py         # System health monitoring
    └── consent.py              # Data collection consent management
```

**Key Classes:**
- `RuntimeState` - Global system state tracking
- `EventBus` - Publish/subscribe event system
- `Scheduler` - Task scheduling with cron support
- `Initializer` - System boot sequence
- `ModuleLoader` - Dynamic module loading

### **jarvis_io/** - Unified I/O Layer
All input/output interfaces consolidated in one package.

```
jarvis_io/
├── __init__.py                # Package exports
├── cli/
│   ├── __init__.py
│   └── interface.py           # AdvancedCLI class with 20+ display methods
├── text/
│   ├── __init__.py
│   ├── input_adapter.py       # CLIInput - text input handling
│   └── output_adapter.py      # TextOutput - text output formatting
├── voice/
│   ├── __init__.py
│   ├── stt.py                 # VoskSTT - offline speech-to-text
│   └── tts.py                 # TTS - pyttsx3 text-to-speech
└── voice_pipeline.py          # VoiceIOPipeline - voice orchestration
```

**Key Classes:**
- `AdvancedCLI` - Rich CLI with colors and formatting
- `CLIInput` - Text input handling
- `TextOutput` - Text output formatting
- `VoskSTT` - Offline speech recognition (Vosk)
- `TTS` - Text-to-speech (pyttsx3)
- `VoiceIOPipeline` - Voice I/O orchestration

### **brain/** - Intelligence Layer
NLU, memory, reasoning, and LLM integration.

```
brain/
├── nlu/
│   ├── __init__.py
│   ├── pipeline.py            # NLUPipeline - intent recognition
│   ├── normalizer.py          # Text normalization
│   ├── entities.py            # Entity extraction
│   └── parser.py              # Intent parser
├── memory/
│   ├── __init__.py
│   ├── storage.py             # JarvisStorage - persistent data
│   ├── context.py             # ContextManager - conversation context
│   └── semantic.py            # Semantic search & embeddings
├── llm/
│   ├── manager.py             # LLMManager - LLM provider interface
│   ├── models/                # Model configurations
│   └── providers/             # Provider implementations
└── reasoning/
    ├── agent.py               # Agent - autonomous decision making
    ├── planner.py             # Planner - multi-step planning
    └── rules.py               # Rule-based reasoning
```

### **skills/** - Skill System
Action executors organized by category.

```
skills/
├── base.py                    # BaseSkill class
├── actions/
│   ├── dispatcher.py          # SkillDispatcher - skill registry & execution
│   ├── base/
│   │   └── skill.py           # Base skill class
│   └── automation/
│       ├── triggers.py        # Event triggers
│       └── rules_engine.py    # Automation rules
├── system/                    # System-level skills
│   ├── logging/
│   │   └── manager.py         # JarvisLogger
│   ├── app_control.py
│   ├── file_ops.py
│   └── os_hooks.py
├── productivity/              # Productivity skills
├── automation/                # Automation skills
├── learning/
│   └── context_awareness.py   # ✨ NEW! Smart context learning
├── analysis/                  # Analysis skills
├── external/                  # External integrations
├── get_time.py
├── system_status.py
├── create_note.py
├── search_file.py
├── reminders.py
└── [15+ other skills]
```

### **data/** - Data Layer
Data collection, storage, and privacy management.

```
data/
├── collector.py               # DataCollector - consent-based data collection
├── storage.py                 # Storage abstraction
├── models.py                  # Data models
└── privacy.py                 # Privacy controls
```

### **monitoring/** - System Monitoring
Logging, metrics, and alerts.

```
monitoring/
├── logger.py                  # JarvisLogger - logging system
├── metrics.py                 # Performance metrics
├── alerts.py                  # Alert system
└── debugger.py                # Debug utilities
```

### **system/** - System Core
Legacy and main engine components.

```
system/
├── core/
│   ├── engine.py              # JarvisCore - main orchestrator
│   ├── runtime_manager.py     # RuntimeManager - runtime management
│   ├── handlers.py            # EventHandlers - event handling
│   └── responses.py           # ResponseFormatter - response formatting
├── consent.py                 # Data consent management
└── [other system files]
```

---

## 🔄 Runtime Lifecycle

### 1. **Boot Sequence**
```python
core.boot()
├── Start EventBus
├── Start Scheduler
├── Run Initializers
├── Load Modules
├── Initialize Voice Pipeline
├── Ready for Commands
└── Emit SYSTEM_BOOT_COMPLETE
```

### 2. **Request Processing**
```
User Input
    ↓
Voice/Text Input Adapter
    ↓
NLU Pipeline (Intent Recognition)
    ↓
Skill Dispatcher (Find matching skill)
    ↓
Skill Execution
    ↓
Context Manager (Update context)
    ↓
Response Formatter
    ↓
Output Adapter (Voice/Text)
    ↓
Context Awareness Recording
```

### 3. **Skill Execution Flow**
```
skill.execute(user_input)
    ├── Parse input
    ├── Access storage/context as needed
    ├── Execute core logic
    ├── Log execution (context awareness)
    ├── Record patterns
    └── Return formatted response
```

---

## 📊 Data Flow

### Event System
```
Event Emitted
    ↓
EventBus.publish(event_type, data)
    ↓
[All Subscribers]
    ├── Handler 1 (records to context)
    ├── Handler 2 (updates metrics)
    ├── Handler 3 (triggers automations)
    └── Handler N
```

### Context Awareness (NEW!)
```
Skill Execution
    ↓
ContextAwareness.record_interaction()
    ├── Track skill usage
    ├── Record time patterns
    ├── Build interaction chain
    ├── Update frequencies
    └── Save to disk
    
User Query → Predict Next Action
    ├── Analyze patterns
    ├── Match current time/day
    ├── Return prediction
    └── Personalize response
```

---

## 🔌 Integration Points

### Adding Skills
```python
# skills/my_category/my_skill.py
from skills.base.skill import Skill

class MySkill(Skill):
    def __init__(self):
        self.name = "my_skill"
        self.description = "What my skill does"
    
    def execute(self, user_input: str) -> str:
        # Your implementation
        return "Response"

# Register in engine.py _register_skills()
"my_skill": MySkill()
```

### Event Subscription
```python
# Subscribe to events
engine.events.subscribe(EVENT_NLU_INTENT, callback)

# Emit events
engine.events.publish(EVENT_NLU_INTENT, {"intent": "open_app", "app": "notepad"})
```

### Custom Modules
```
modules/installed/my_module/
├── module.py
└── __init__.py

# module.py must define:
def setup(core):
    """Initialize module, return object with stop() method"""
    return MyModule(core)
```

---

## ⚙️ Configuration

**File:** `jarvis/config.json`

```json
{
  "name": "Jarvis",
  "version": "0.0.4",
  "voice_enabled": true,
  "wake_word": "jarvis",
  "data_collection": false,
  "debug_nlu": false,
  "workers": 4,
  "short_term_memory_max": 20,
  "fallback_to_cli": true,
  "use_colors": true
}
```

---

## 🔐 Privacy & Consent

- **Opt-in data collection** - Users control data sharing
- **Consent management** - Explicit user consent required
- **Privacy controls** - Granular privacy settings
- **Secure storage** - Encrypted data storage
- **Transparent logging** - Clear logging of data access

---

## 📈 Performance Characteristics

| Metric | Target | Actual |
|--------|--------|--------|
| Boot Time | <3s | ~2-3s |
| Skill Response | <500ms | <400ms |
| Memory Usage | <200MB | ~150MB |
| Event Processing | <10ms | <5ms |
| Concurrent Skills | 4 | Configurable |

---

## 🛠️ Extension Points

1. **Skills** - Add new capabilities
2. **Event Handlers** - React to system events
3. **Modules** - Dynamic plugin system
4. **Providers** - LLM/API integrations
5. **Formatters** - Custom output formatting
6. **Validators** - Input validation rules

---
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