import random
import time
import os
import re
from wakeonlan import send_magic_packet

# Configuración predeterminada
min_delay = 6  # Mínimo de segundos entre intentos
max_delay = 40  # Máximo de segundos entre intentos
target_range = (1, 10)  # Rango objetivo para activar el encendido


def detect_mac_address():
    """
    Detecta automáticamente la dirección MAC de la tarjeta de red principal.
    Retorna la primera dirección MAC encontrada o None si no detecta ninguna.
    """
    print("Detectando dirección MAC...")
    try:
        if os.name == 'nt':  # Windows
            command = "getmac"
        else:  # Linux/Mac
            command = "ip addr"

        result = os.popen(command).read()
        mac_address = None

        # Expresión regular para buscar direcciones MAC
        mac_regex = re.compile(r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}")

        # Buscar la primera coincidencia
        match = mac_regex.search(result)
        if match:
            mac_address = match.group(0)

        if mac_address:
            print(f"Dirección MAC detectada: {mac_address}")
        else:
            print("No se pudo detectar automáticamente una dirección MAC válida.")
        return mac_address
    except Exception as e:
        print(f"Error al detectar la dirección MAC: {e}")
        return None


def enable_wol():
    """
    Intenta habilitar el soporte para Wake-on-LAN automáticamente en la tarjeta de red principal.
    """
    print("Intentando habilitar Wake-on-LAN automáticamente...")
    try:
        if os.name == 'nt':  # Windows
            print("En Windows, habilita WoL desde el Administrador de dispositivos si no está activado.")
            return True  # No hay una forma directa con comandos para habilitar WoL en Windows desde Python.
        else:  # Linux/Mac
            # Comando para habilitar WoL en Linux/Mac usando ethtool
            command_check = "ip link | grep 'state UP' | awk '{print $2}' | sed 's/://' "
            interface = os.popen(command_check).read().strip()

            if interface:
                print(f"Interfaz detectada: {interface}")
                enable_command = f"sudo ethtool -s {interface} wol g"
                result = os.system(enable_command)
                if result == 0:
                    print("Wake-on-LAN habilitado con éxito.")
                    return True
                else:
                    print("Error al habilitar Wake-on-LAN. Asegúrate de tener permisos de administrador.")
                    return False
            else:
                print("No se detectó una interfaz de red activa.")
                return False
    except Exception as e:
        print(f"Error al intentar habilitar WoL: {e}")
        return False


def generate_random_and_check(mac_address):
    """
    Genera un número aleatorio y verifica si está dentro del rango objetivo.
    Si el número está en rango, envía un paquete WoL.
    """
    number = random.randint(1, 100)  # Genera un número aleatorio entre 1 y 100
    print(f"Número generado: {number}")
    if target_range[0] <= number <= target_range[1]:
        print("Número en rango. Enviando paquete WoL...")
        send_magic_packet(mac_address)
    else:
        print("Número fuera de rango. Esperando próximo intento...")


def main():
    # Detectar dirección MAC automáticamente
    mac_address = detect_mac_address()
    if not mac_address:
        print("No se puede continuar sin una dirección MAC válida.")
        return

    # Intentar habilitar soporte para WoL
    if not enable_wol():
        print("No se pudo habilitar Wake-on-LAN automáticamente. Revisa las configuraciones.")
        return

    print("Iniciando el programa...")
    while True:
        # Generar número aleatorio y verificar rango
        generate_random_and_check(mac_address)
        # Pausar entre intentos con un tiempo aleatorio
        delay = random.randint(min_delay, max_delay)
        print(f"Esperando {delay} segundos...")
        time.sleep(delay)


if __name__ == "__main__":
    main()
