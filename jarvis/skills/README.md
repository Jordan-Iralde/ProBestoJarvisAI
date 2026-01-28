# 🎯 Skills Directory

Directorio centralizado de todas las 17 skills disponibles en JarvisAI.

---

## 🏗️ **Estructura de Skills**

```
skills/
├── system/              # Sistema & Hardware (8 skills)
├── productivity/        # Productividad (3 skills)
├── automation/          # Automatización (1 skill)
├── analysis/            # Análisis (3 skills)
├── learning/            # Aprendizaje (2 skills)
├── research/            # Investigación (4 skills)
├── external/            # Integraciones externas (vacío)
└── actions/             # Dispatcher (1 módulo)
```

---

## 🖥️ **System Skills** (8)
Gestión del sistema, estado y optimización.

| Skill | Descripción |
|---|---|
| `analyze_system_health.py` | Analiza salud del sistema (CPU, RAM, disco) |
| `system_status.py` | Status general del hardware y software |
| `system_auto_optimization.py` | Optimizaciones automáticas del sistema |
| `get_time.py` | Obtiene hora/fecha actual |
| `what_do_you_know_about_me.py` | Análisis del perfil del usuario |
| `app_control.py` | Control de aplicaciones |
| `file_ops.py` | Operaciones de archivos |
| `os_hooks.py` | Hooks del SO (sistema operativo) |

---

## 📝 **Productivity Skills** (3)
Tareas de día a día y gestión.

| Skill | Descripción |
|---|---|
| `create_note.py` | Crear notas y guardarlas |
| `reminders.py` | Gestionar recordatorios |
| `open_app.py` | Abrir aplicaciones |

---

## ⚙️ **Automation Skills** (1)
Automatización inteligente de procesos.

| Skill | Descripción |
|---|---|
| `auto_programming.py` | Programación automática de workflows |

---

## 📊 **Analysis Skills** (3)
Análisis de datos e interacciones.

| Skill | Descripción |
|---|---|
| `analyze_session_value.py` | Valida sesiones de usuario |
| `evaluate_user_session.py` | Evalúa valor de sesiones |
| `research_and_contextualize.py` | Contextualiza investigaciones |

---

## 🧠 **Learning Skills** (2)
Aprendizaje automático y adaptación.

| Skill | Descripción |
|---|---|
| `learning_engine.py` | Motor principal de aprendizaje |
| `context_awareness.py` | **[NEW]** Aprende patrones de interacción |

---

## 🔍 **Research Skills** (4)
Investigación y búsqueda de información.

| Skill | Descripción |
|---|---|
| `research_skill.py` | Investigación general |
| `search_file.py` | Búsqueda de archivos |
| `summarize_recent_activity.py` | Resume actividad reciente |
| `summarize_last_session.py` | Resume última sesión |

---

## 🔧 **Actions Module** (1)
Dispatcher y orquestador de skills.

| Módulo | Descripción |
|---|---|
| `dispatcher.py` | Ejecuta skills basado en intención |

---

## 📈 **Estadísticas**

```
Total Skills:       17
Categorías:         6
Líneas de código:   ~5000
Pruebas:            22/22 pasando ✓
Status:             PRODUCTION READY ✓
```

---

## 🚀 **Usar un Skill**

Desde CLI:
```
> ¿Qué hora es?
> Abre notepad
> Estado del sistema
> Crea una nota
```

Desde Python:
```python
from system.core import JarvisCore

core = JarvisCore()
result = core.dispatch_intent("ask_time", {})
```

---

## 📖 **Documentación Relacionada**

- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) - Cómo funcionan los skills
- [docs/API.md](../docs/API.md) - APIs disponibles
- [docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md) - Crear nuevos skills

---

## ✏️ **Crear un Nuevo Skill**

1. **Crea archivo:**
   ```python
   # skills/category/new_skill.py
   from skills.actions.base.skill import Skill
   
   class NewSkill(Skill):
       def run(self, entities, system_state):
           # Tu lógica aquí
           return {"response": "Done!"}
   ```

2. **Regístralo en `system/core/engine.py`:**
   ```python
   def _register_skills(self):
       # ... existing skills ...
       self.skills["new_skill"] = NewSkill()
   ```

3. **Prueba:**
   ```python
   python tests_verify/verify_phase_8_final.py
   ```

---

<div align="center">

**¡17 Skills listos para automatizar tu vida!** 🚀

v0.0.4 • MIT License

</div>
