1️⃣ Principios del roadmap (no negociables)

Estas reglas explican por qué el roadmap es así:

🔒 Estabilidad > Inteligencia bruta

Un asistente que “a veces entiende” pero siempre explica vale más que uno inteligente pero opaco.

👁️ Inteligencia visible

Cada release debe hacer que el usuario:

“entienda qué pensó Jarvis y por qué hizo lo que hizo”

🔁 Loop completo en cada versión
Input → Interpretación → Acción → Reflexión → Mejora perceptible

🧱 Escalabilidad por capas

Nada de features que:

rompan contratos

obliguen a refactors masivos

mezclen ejecución con razonamiento

2️⃣ Rol de cada versión (visión global)
Versión	Rol
v0.0.4	Estabilización + Observabilidad
v0.0.5	Comprensión explicable
v0.0.6	Memoria útil y perfilado
v0.0.7	Reflexión y recomendaciones
v0.0.8	Autonomía supervisada
v0.1.0	Producto alfa serio
3️⃣ Roadmap detallado
🔵 v0.0.4 — “Stability & Clarity Release”

Objetivo: Sistema sólido, entendible, confiable

Qué DEBE tener (obligatorio)
Core & Infra

 Hardening de error handling (excepciones específicas)

 Validación estricta de config (schema)

 Health checks por componente

 Graceful degradation real (no crashes)

CLI (muy importante)

 Modo --debug

 NLU Trace visible

 Confidence score por intent

 Errores con causa + sugerencia

Brain

 ContextManager usado SIEMPRE en NLU

 Reflexión post-skill (solo lectura)

 Registro de decisiones (por qué hizo X)

Docs

 ARCHITECTURE actualizado

 “How Jarvis thinks” (conceptual)

 Guía de contribución a skills

 CHANGELOG formal

NO incluir

❌ ML complejo
❌ Autonomía
❌ Auto-programación

📌 Valor visible:
Jarvis ahora explica lo que entiende y no sorprende con errores raros.

🟢 v0.0.5 — “Explainable Intelligence”

Objetivo: Que Jarvis parezca inteligente aunque todavía sea simple

Features clave
NLU

 Intent confidence threshold

 Intent ambiguity handling

 “Creo que quisiste decir…” (top 2 intents)

 Spell correction básica

CLI UX

 Respuesta estructurada:

Interpretación

Acción

Resultado

 Modo why:

> why
→ Porque detecté intent X con 0.73 de confianza

Skills

 Metadata por skill (qué hace, riesgos)

 Pre-checks de ejecución

 Tiempo estimado de ejecución

📌 Valor visible:
Jarvis razona en voz alta.

🟡 v0.0.6 — “Memory That Matters”

Objetivo: Memoria útil, no solo persistente

Features clave
Memory

 Short-term vs long-term memory

 Consolidación automática

 Confidence-weighted facts

 Pruning inteligente

User Profile

 what_do_you_know_about_me

 Preferencias detectadas (horarios, comandos)

 Historial resumido por sesiones

Skills nuevas

 summarize_week

 patterns_detected

 frequent_actions

📌 Valor visible:
Jarvis recuerda patrones, no solo frases.

🟠 v0.0.7 — “Reflection & Recommendation”

Objetivo: Jarvis empieza a ayudar proactivamente (sin ejecutar)

Features clave
Reflection Engine

 Análisis de sesiones

 Detección de fricción

 Reglas de mejora

Recomendaciones

 “Podrías automatizar X”

 “Hiciste esto 5 veces esta semana”

 “Esto falló 3 veces”

Seguridad

 Ninguna acción automática

 Todo pasa por aprobación explícita

📌 Valor visible:
Jarvis piensa sobre tu forma de trabajar.

🔴 v0.0.8 — “Supervised Autonomy”

Objetivo: Empezar autonomía sin perder control

Features clave
Planning

 Descomposición de objetivos

 Plan → aprobación → ejecución

 Simulación de plan antes de ejecutar

Control del sistema

 Acciones con permisos

 Modo dry-run

 Logs de impacto

CLI

 “Ejecutar plan”

 “Cancelar”

 “Mostrar consecuencias”

📌 Valor visible:
Jarvis ayuda a decidir y ejecutar, no actúa solo.

🟣 v0.1.0 — “Serious Alpha”

Objetivo: Producto usable por terceros técnicos

Requisitos mínimos
Producto

 CLI robusta

 Voice estable

 Multi-session real

 Estado persistente confiable

Ingeniería

 API interna estable

 Versioning semántico

 Tests de regresión

 Benchmarks automáticos

Seguridad

 Roles

 Auditoría

 Safe defaults

📌 Resultado:
JarvisAI deja de ser “proyecto interesante” y pasa a ser producto alfa serio.

4️⃣ Definition of Done (para TODAS las versiones)

Una versión NO se libera si no cumple:

✔ Boot sin warnings

✔ Tests pasando

✔ Docs actualizadas

✔ Valor observable desde CLI

✔ Ninguna feature “a medias”

✔ Sin deuda escondida

5️⃣ Riesgos a evitar (muy importante)

❌ Meter ML “porque sí”
❌ Autonomía sin trazabilidad
❌ UX pobre en CLI
❌ Features sin explicación
❌ Refactors grandes sin necesidad