#!/bin/bash

echo "🧠 Instalador de dependencias para JarvisAI"

# Paso 1: Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
  echo "[+] Creando entorno virtual..."
  python3 -m venv venv
else
  echo "[✓] Entorno virtual ya existe."
fi

# Paso 2: Activar entorno virtual
echo "[+] Activando entorno virtual..."
source venv/bin/activate || source venv/Scripts/activate

# Paso 3: Instalar dependencias
if [ -f "scripts/requirements.txt" ]; then
  echo "[+] Instalando dependencias desde requirements.txt..."
  pip install --upgrade pip
  pip install -r scripts/requirements.txt
else
  echo "[ERROR] No se encontró scripts/requirements.txt"
  exit 1
fi

# Paso 4: Crear archivo .env si no existe
if [ ! -f ".env" ]; then
  echo "[+] Generando archivo .env desde .env.example..."
  cp .env.example .env
fi

echo "[✅] Instalación completa. Ejecutá Jarvis con: python main.py"
