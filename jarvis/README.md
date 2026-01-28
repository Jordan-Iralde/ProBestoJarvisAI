# 🌐 **JarvisAI v0.0.4**

## Quick Links to Documentation
- **[📖 Full Documentation](./docs/architecture.md)** - Complete system design and modules
- **[🔌 API Reference](./docs/api.md)** - Core APIs and integration points  
- **[🛠️ Contributing Guide](./docs/CONTRIBUTING.md)** - Development and contribution standards

---

## **✨ Key Features - v0.0.4**

### 🧠 **Smart Context Awareness** (NEW!)
Jarvis now learns from your interaction patterns and predicts your next actions:
- Tracks usage by time of day
- Identifies common task sequences  
- Suggests workflow automation
- Personalizes system responses

Example:
```
You: "Suggest optimization"
Jarvis: "Consider automating search_file + get_time workflow for faster execution"
```

### 🎯 **Core Capabilities**
- **Voice I/O**: Offline Vosk STT + pyttsx3 TTS
- **NLU Pipeline**: Intent recognition and entity extraction
- **17+ Skills**: Across 5 functional categories
- **Privacy-First**: Consent-based data collection
- **Active Learning**: Learns from every interaction
- **Multi-Session**: Manage multiple conversations

---

## **🚀 Quick Start**

### Installation
```bash
pip install -r requirements.txt
cd jarvis
python main.py
```

### Verify System
```bash
# Quick test (10 import tests)
python verify_phase_7_8.py

# Full system test (22 tests)  
python verify_phase_8_final.py
```

---

## **📁 Project Structure**

```
jarvis/
├── core/              # Core lifecycle & boot components
├── jarvis_io/         # Unified I/O layer (CLI, text, voice)
├── brain/             # NLU, memory, reasoning, LLM
├── skills/            # 17+ skills in 5 categories
│   ├── system/        # System operations
│   ├── productivity/  # Productivity tools
│   ├── automation/    # Task automation
│   ├── analysis/      # Analysis & insights
│   └── learning/      # Learning features (context_awareness)
├── data/              # Data collection & storage
└── monitoring/        # Logging & metrics
```

---

## **⚙️ Configuration**

Edit `jarvis/config.json`:
```json
{
  "name": "Jarvis",
  "version": "0.0.4",
  "voice_enabled": true,
  "wake_word": "jarvis",
  "data_collection": false,
  "debug_nlu": false
}
```

---

## **📚 Documentation Files (4-File Standard)**

### 1. **README.md** (this file)
- Overview and quick start
- Feature highlights
- Quick reference

### 2. **[docs/ARCHITECTURE.md](./docs/architecture.md)**
- Complete system design
- Module descriptions
- Data flow and runtime lifecycle

### 3. **[docs/API.md](./docs/api.md)**
- Core class references
- Method documentation
- Integration interfaces

### 4. **[docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md)**
- Development guidelines
- Code standards
- Testing requirements
- Contribution process

---

## **🔄 Recent Updates**

✅ **v0.0.4 Refactoring Complete**
- Added Smart Context Awareness (NEW!)
- Fixed VoskSTT `is_available()` method
- Enhanced module loader error handling
- 100% system test pass rate
- Reorganized documentation to 4-file standard

---

## **📊 Status**

| Metric | Value |
|--------|-------|
| System Tests | 22/22 ✅ |
| Skills Registered | 17+ |
| Import Chain | 100% Working |
| Voice I/O | Operational |
| Context Awareness | ✨ NEW! |

**Status**: Production Ready with Smart Context Awareness

---

## **📖 Next Steps**

1. **Read**: Check [ARCHITECTURE.md](./docs/architecture.md) for system design
2. **Integrate**: See [API.md](./docs/api.md) for integration points
3. **Contribute**: Follow [CONTRIBUTING.md](./docs/CONTRIBUTING.md) guidelines
4. **Learn**: Try the context awareness feature - ask about your patterns!

---

- El modelo se divide en dos componentes:
  - **JAR:** Focalizado en la interacción natural, traducción en tiempo real, aprendizaje autónomo mediante una backdoor, reconocimiento facial y generación de ideas.
  - **VIS:** Enfocado en la generación de código, entrenamiento reforzado y optimización automática.

### **Fase 3: Optimización de Códigos**
**Objetivo:** Mejorar la eficiencia del código, optimizar el sistema operativo y aprender de contextos complejos.

- Integración con entornos de juegos y situaciones reales para entrenar la IA en la resolución de problemas complejos.
- Habilidad para resolver problemas de alta complejidad y optimizar el sistema sin intervención externa.

---

## **🛠️ Instalación y Configuración**

Para comenzar con el proyecto, ejecuta el siguiente script para instalar todas las dependencias necesarias:

```bash
python InstalarDependencias.py
```
## **📈 Mejora Continua y Futuro del Proyecto**
Este proyecto está diseñado para evolucionar y adaptarse constantemente. A medida que avances, encontrarás nuevas actualizaciones y mejoras que permiten integrar capacidades como **decisiones autónomas**, **entornos distribuidos**, y **colaboración entre IA**. Los próximos pasos incluyen expandir la capacidad de la IA para integrarse en más plataformas y dispositivos.

---

## **📚 Documentación y Recursos Adicionales**
Consulta la documentación completa para obtener más detalles y orientación técnica.

---

## **📬 Contribuciones**
¡Este proyecto es **abierto** y **colaborativo**! Si tienes sugerencias, mejoras o encuentras algún problema, no dudes en abrir un **issue** o enviar un **pull request**. Tu contribución es muy valiosa.

---

## **  >>> Estado Actual Desarrollo**
El proyecto se encuentra en **Desarrollo**. 
---

## **🌐 Licencia**
Este proyecto está licenciado bajo la **Licencia MIT**.

Visita la pagina de Jarvis (En desarrollo) : https://jordan-iralde.github.io/ProBestoJarvisAI/ 

