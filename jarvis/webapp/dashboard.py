# webapp/dashboard.py
"""
Jarvis Web Dashboard - Interfaz visual para monitoreo y control
Proporciona una interfaz web para interactuar con Jarvis.
"""

from flask import Flask, render_template, request, jsonify
import json
import time
from datetime import datetime
import threading
import os

class JarvisDashboard:
    """Web dashboard para Jarvis"""

    def __init__(self, core_instance):
        self.core = core_instance
        self.app = Flask(__name__,
                        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                        static_folder=os.path.join(os.path.dirname(__file__), 'static'))
        self._setup_routes()
        self.server_thread = None

    def _setup_routes(self):
        """Configurar rutas del dashboard"""

        @self.app.route('/')
        def index():
            """Página principal del dashboard"""
            return render_template('index.html')

        @self.app.route('/api/status')
        def api_status():
            """API endpoint para estado del sistema"""
            try:
                # Obtener estado del sistema
                health = self.core.skill_dispatcher.dispatch("analyze_system_health", "general")
                insights = self.core.get_session_insights()

                return jsonify({
                    "status": "online",
                    "timestamp": datetime.now().isoformat(),
                    "system_health": health.get("analysis", {}) if health and health.get("success") else {},
                    "session_insights": insights,
                    "uptime": time.time() - self.core.start_time,
                    "skills_count": len(self.core.skill_dispatcher.skills)
                })
            except Exception as e:
                return jsonify({"status": "error", "error": str(e)}), 500

        @self.app.route('/api/command', methods=['POST'])
        def api_command():
            """API endpoint para ejecutar comandos"""
            try:
                data = request.get_json()
                command = data.get('command', '').strip()
                skill = data.get('skill', 'auto')
                params = data.get('params', {})

                if not command:
                    return jsonify({"success": False, "error": "No command provided"}), 400

                # Ejecutar comando
                if skill == 'auto':
                    # Intentar detectar skill automáticamente
                    result = self._process_command_auto(command)
                else:
                    # Usar skill específico
                    result = self.core.skill_dispatcher.dispatch(skill, command, params)

                return jsonify(result)

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route('/api/skills')
        def api_skills():
            """API endpoint para listar skills disponibles"""
            try:
                skills = {}
                for name, skill_class in self.core.skill_dispatcher.skills.items():
                    skills[name] = {
                        "name": name,
                        "description": getattr(skill_class, '__doc__', 'No description').strip(),
                        "methods": [method for method in dir(skill_class) if not method.startswith('_')]
                    }

                return jsonify({"skills": skills})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/api/auto_optimize')
        def api_auto_optimize():
            """API endpoint para optimización automática"""
            try:
                result = self.core.skill_dispatcher.dispatch("system_auto_optimization", "full_optimization")
                return jsonify(result)
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

    def _process_command_auto(self, command: str) -> dict:
        """Procesar comando automáticamente detectando el skill apropiado"""
        try:
            # Usar NLU para detectar intent
            if self.core.nlu:
                self.core.nlu.process(command, self.core.events)
                # Esperar un poco para que se procese
                time.sleep(0.1)

                # Por ahora, fallback simple basado en keywords
                command_lower = command.lower()

                if any(word in command_lower for word in ['hora', 'time', 'fecha']):
                    return self.core.skill_dispatcher.dispatch("get_time", "run")
                elif any(word in command_lower for word in ['optimizar', 'limpiar', 'tune']):
                    return self.core.skill_dispatcher.dispatch("system_auto_optimization", "full_optimization")
                elif any(word in command_lower for word in ['estado', 'status']):
                    return self.core.skill_dispatcher.dispatch("system_status", "run")
                elif any(word in command_lower for word in ['nota', 'anota']):
                    return self.core.skill_dispatcher.dispatch("create_note", "run", {"text": command})
                else:
                    return {"success": False, "error": f"Comando no reconocido: {command}"}
            else:
                return {"success": False, "error": "NLU no disponible"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def start(self, host='localhost', port=5000):
        """Iniciar el servidor web"""
        def run_server():
            self.app.run(host=host, port=port, debug=False, use_reloader=False)

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

        print(f"🌐 Dashboard iniciado en http://{host}:{port}")
        return True

    def stop(self):
        """Detener el servidor web"""
        if self.server_thread:
            # Flask no tiene shutdown directo, pero el thread daemon se detendrá con la app
            pass