# JarvisAI v0.0.4 - API Reference

> Complete API documentation for core classes and integration points

---

## 🔌 Core APIs

### **JarvisCore** - Main Engine
Central orchestrator managing all system components.

```python
from system.core import JarvisCore

# Initialize
core = JarvisCore(config)

# Boot the system
core.boot()

# Process input
response = core.run()  # Interactive loop

# Stop gracefully
core.stop()
```

**Key Methods:**
- `boot()` - Start system boot sequence
- `run()` - Main event loop
- `stop()` - Graceful shutdown
- `_register_skills()` - Register all skills
- `_log(tag, msg)` - Internal logging

**Key Attributes:**
- `events: EventBus` - Event system
- `scheduler: Scheduler` - Task scheduler
- `skill_dispatcher: SkillDispatcher` - Skill execution
- `nlu: NLUPipeline` - Intent recognition
- `storage: JarvisStorage` - Persistent storage
- `voice_pipeline: VoiceIOPipeline` - Voice I/O
- `context_manager: ContextManager` - Conversation context

---

### **EventBus** - Event System
Publish/subscribe event system for component communication.

```python
from core.lifecycle.runtime import EventBus
from core.constants import EVENT_NLU_INTENT

bus = EventBus(workers=4)

# Subscribe to events
def handle_intent(data):
    print(f"Intent: {data['intent']}")

bus.subscribe(EVENT_NLU_INTENT, handle_intent)

# Publish events
bus.publish(EVENT_NLU_INTENT, {
    "intent": "open_app",
    "app": "notepad",
    "confidence": 0.95
})

# Unsubscribe
bus.unsubscribe(EVENT_NLU_INTENT, handle_intent)
```

**Key Methods:**
- `subscribe(event_type, callback)` - Register listener
- `unsubscribe(event_type, callback)` - Remove listener
- `publish(event_type, data)` - Emit event
- `start()` - Start event processing
- `stop()` - Stop event processing

**Built-in Events:**
- `EVENT_NLU_INTENT` - Intent recognized
- `EVENT_INPUT_TEXT` - Text input received
- `EVENT_INPUT_VOICE` - Voice input received
- `EVENT_JARVIS_RESPONSE` - Response generated

---

### **SkillDispatcher** - Skill Execution
Manages skill registration and execution.

```python
from skills.actions.dispatcher import SkillDispatcher

dispatcher = SkillDispatcher()

# Register skill
dispatcher.register("my_skill", MySkillInstance)

# Execute skill
result = dispatcher.execute("my_skill", user_input)

# List available skills
skills = dispatcher.list_skills()
```

**Key Methods:**
- `register(name, skill)` - Register skill
- `execute(name, input)` - Execute skill
- `list_skills()` - Get available skills
- `get_skill(name)` - Get skill instance

---

### **NLUPipeline** - Intent Recognition
Natural language understanding and intent extraction.

```python
from brain.nlu.pipeline import NLUPipeline

nlu = NLUPipeline(skills, debug=False)

# Parse user input
intent_data = nlu.parse("open notepad")
# Returns: {"intent": "open_app", "app": "notepad", "confidence": 0.92}

# Extract entities
entities = nlu.extract_entities("set reminder for 3 PM")
# Returns: [{"type": "time", "value": "3 PM"}]
```

**Key Methods:**
- `parse(text)` - Recognize intent
- `extract_entities(text)` - Extract named entities
- `normalize(text)` - Normalize text

**Returns:**
```python
{
    "intent": "skill_name",
    "confidence": 0.92,
    "entities": [...],
    "original": "user input"
}
```

---

### **ContextAwareness** - Pattern Learning (NEW!)
Learn from interaction patterns and predict next actions.

```python
from skills.learning.context_awareness import ContextAwareness

aware = ContextAwareness()

# Record interaction
aware.record_interaction(
    skill_name="search_file",
    input_text="find my documents",
    output_text="Found 5 files"
)

# Get context summary
context = aware.get_context_summary()
# Returns: {
#   "current_hour": 14,
#   "current_day": "Wednesday", 
#   "top_skills": [...],
#   "likely_next_skills": [...]
# }

# Predict next action
next_skill = aware.predict_next_action()

# Get personalized message
msg = aware.get_personalized_message("Your files are ready")

# Identify workflow patterns
workflow = aware.identify_workflow()

# Get optimization suggestions
suggestion = aware.suggest_optimization()
```

**Key Methods:**
- `record_interaction(skill, input, output)` - Record usage
- `get_context_summary()` - Get usage overview
- `predict_next_action()` - Predict next skill
- `get_personalized_message(msg)` - Personalize response
- `identify_workflow()` - Find common patterns
- `suggest_optimization()` - Suggest automations

---

### **VoiceIOPipeline** - Voice I/O
Orchestrate speech-to-text and text-to-speech.

```python
from jarvis_io.voice_pipeline import VoiceIOPipeline

pipeline = VoiceIOPipeline(config)

# Set event bus
pipeline.set_eventbus(core.events)

# Set voice callback
def on_voice(recognized_text):
    print(f"User said: {recognized_text}")

pipeline.set_voice_callback(on_voice)

# Start voice listening
if pipeline.start():
    print("Voice pipeline started")

# Send TTS output
pipeline.tts.speak("Hello, I'm Jarvis")

# Stop
pipeline.stop()
```

**Key Methods:**
- `start()` - Start voice pipeline
- `stop()` - Stop voice pipeline
- `set_eventbus(bus)` - Set event system
- `set_voice_callback(callback)` - Set voice handler

**Key Attributes:**
- `stt: VoskSTT` - Speech-to-text
- `tts: TTS` - Text-to-speech
- `_running` - Pipeline status

---

### **ContextManager** - Conversation Context
Manage conversation context and history.

```python
from brain.memory.context import ContextManager
from brain.memory.storage import JarvisStorage

storage = JarvisStorage()
context_mgr = ContextManager(storage)

# Add context
context_mgr.add_context({
    "user": "Jordan",
    "topic": "file search",
    "files_found": 5
})

# Get context
ctx = context_mgr.get_context()

# Clear context (new conversation)
context_mgr.clear()

# Get recent interactions
recent = context_mgr.get_recent(count=5)
```

**Key Methods:**
- `add_context(data)` - Add to context
- `get_context()` - Get current context
- `clear()` - Clear context
- `get_recent(count)` - Get recent interactions

---

### **Scheduler** - Task Scheduling
Schedule and manage recurring tasks.

```python
from core.lifecycle.runtime import Scheduler

scheduler = Scheduler()

# Schedule one-time task
scheduler.schedule_once(5.0, callback_fn, args=(arg1, arg2))

# Schedule recurring task (every N seconds)
scheduler.schedule_every(60.0, periodic_fn)

# Schedule cron-style task
scheduler.schedule_cron("0 9 * * *", morning_fn)  # 9 AM daily

# Start scheduler
scheduler.start()

# Stop
scheduler.stop()
```

**Key Methods:**
- `schedule_once(delay, fn, args)` - One-time execution
- `schedule_every(interval, fn, args)` - Recurring task
- `schedule_cron(pattern, fn, args)` - Cron-style scheduling
- `start()` - Start scheduler
- `stop()` - Stop scheduler

---

## 🛠️ Skill Development API

### **BaseSkill** - Skill Base Class
Base class for all skills.

```python
from skills.base.skill import Skill

class MySkill(Skill):
    def __init__(self):
        self.name = "my_skill"
        self.description = "What my skill does"
        self.keywords = ["keyword1", "keyword2"]
    
    def execute(self, user_input: str, **kwargs) -> str:
        """Execute the skill and return response"""
        # Your implementation
        return "Response text"
    
    def validate(self, user_input: str) -> bool:
        """Validate if this skill should handle the input"""
        return True
```

**Key Methods:**
- `execute(user_input, **kwargs)` - Execute skill (required)
- `validate(user_input)` - Check if applicable (optional)

**Accessing Core Features:**
```python
class MySkill(Skill):
    def execute(self, user_input, core=None):
        if core:
            # Access storage
            data = core.storage.get("key")
            
            # Log information
            core.logger.logger.info(f"Executing {self.name}")
            
            # Emit events
            core.events.publish("MY_EVENT", {"data": "value"})
            
            # Access context
            context = core.context_manager.get_context()
        
        return "Response"
```

---

## 📊 Data Structures

### **Intent Data**
```python
{
    "intent": "open_app",          # Matched intent/skill
    "confidence": 0.92,             # Confidence score (0-1)
    "entities": [                   # Extracted entities
        {
            "type": "app_name",
            "value": "notepad",
            "confidence": 0.95
        }
    ],
    "original": "open notepad"      # Original user input
}
```

### **Event Data**
```python
# Example: NLU_INTENT event
{
    "intent": "open_app",
    "app": "notepad",
    "confidence": 0.95,
    "timestamp": "2026-01-23T14:30:00",
    "session_id": "sess_abc123"
}
```

### **Context Data**
```python
{
    "current_hour": 14,
    "current_day": "Wednesday",
    "top_skills": [
        {"name": "get_time", "usage_count": 47},
        {"name": "search_file", "usage_count": 23}
    ],
    "likely_next_skills": ["get_time", "create_note"],
    "total_interactions": 156
}
```

---

## 🔐 Error Handling

### **Try-Catch Pattern**
```python
try:
    result = skill_dispatcher.execute("my_skill", user_input)
except Exception as e:
    logger.error(f"Skill execution failed: {e}")
    return fallback_response
```

### **Event Error Handling**
```python
def safe_handler(data):
    try:
        # Process event
        pass
    except Exception as e:
        logger.error(f"Event handler failed: {e}")
        # Emit error event
        bus.publish("ERROR", {"error": str(e)})

bus.subscribe(EVENT_NLU_INTENT, safe_handler)
```

---

## 🚀 Common Integration Patterns

### **Create Custom Skill**
```python
# skills/my_category/my_skill.py
from skills.base.skill import Skill

class MySkill(Skill):
    def __init__(self):
        self.name = "my_skill"
        self.description = "Does something useful"
    
    def execute(self, user_input, core=None):
        # Implementation
        return "Done"

# Register in engine.py
"my_skill": MySkill()
```

### **Listen to Events**
```python
def on_intent(data):
    if data["intent"] == "my_skill":
        print(f"My skill was triggered with: {data}")

core.events.subscribe(EVENT_NLU_INTENT, on_intent)
```

### **Access Persistent Data**
```python
# Save data
core.storage.set("user_prefs", {"theme": "dark"})

# Retrieve data
prefs = core.storage.get("user_prefs")

# Delete data
core.storage.delete("user_prefs")
```

### **Schedule Tasks**
```python
# Run once after 30 seconds
core.scheduler.schedule_once(30, cleanup_fn)

# Run every hour
core.scheduler.schedule_every(3600, hourly_task)

# Run at specific time (9 AM daily)
core.scheduler.schedule_cron("0 9 * * *", morning_task)
```

---

## 📝 Configuration Reference

**Available Config Keys:**
```json
{
  "name": "Jarvis",                 # System name
  "version": "0.0.4",              # Version
  "voice_enabled": true,           # Enable voice I/O
  "wake_word": "jarvis",           # Voice wake word
  "data_collection": false,        # Enable data collection
  "debug_nlu": false,              # Debug NLU
  "workers": 4,                    # Event workers
  "short_term_memory_max": 20,    # Memory limit
  "fallback_to_cli": true,         # Fallback when voice unavailable
  "use_colors": true,              # Colored CLI output
  "log_level": "INFO"              # Logging level
}
```

---

## 🆘 Troubleshooting

**Issue:** Skill not found
- Check skill is registered in `_register_skills()`
- Verify skill name matches dispatcher call

**Issue:** Voice pipeline fails
- Ensure Vosk model is installed
- Check `VoskSTT.is_available()` returns True
- Enable fallback to CLI in config

**Issue:** Events not processing
- Verify subscriber is properly registered
- Check event bus is started
- Confirm event type matches subscription

**Issue:** Skills slow to respond
- Check skill logic for blocking operations
- Consider using async operations
- Monitor scheduler worker count

---

**Last Updated:** January 23, 2026
**Version:** 0.0.4
