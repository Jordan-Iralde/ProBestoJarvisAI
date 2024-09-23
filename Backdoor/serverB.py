import socket
import subprocess
import os

def handle_commands():
    # Obtener el directorio actual del servidor y enviarlo al cliente
    current_dir = os.getcwd()
    client_socket.send(current_dir.encode("utf-8"))

    while True:
        # Recibir el comando del cliente
        command = client_socket.recv(3000).decode("utf-8")
        
        # Si el cliente envía "exit", cerrar la conexión
        if command.lower() == "exit":
            print("Conexión cerrada por el cliente.")
            break

        # Si es un comando para cambiar de directorio (cd)
        elif command.startswith("cd"):
            try:
                # Cambiar al nuevo directorio
                os.chdir(command[3:])
                new_dir = os.getcwd()
                client_socket.send(new_dir.encode("utf-8"))
            except FileNotFoundError as e:
                # Enviar error si el directorio no existe
                client_socket.send(f"Error: {str(e)}".encode("utf-8"))

        # Si el comando es ejecutar un programa en Python
        elif command == "run python hello":
            try:
                # Ejecutar el programa que imprime "Hola Mundo"
                result = subprocess.run(['python3', '-c', 'print("Hola Mundo")'], capture_output=True, text=True)
                client_socket.send(result.stdout.encode("utf-8"))
            except Exception as e:
                client_socket.send(f"Error al ejecutar: {str(e)}".encode("utf-8"))

        # Para otros comandos, ejecutarlos en la shell del sistema
        else:
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                # Enviar el resultado de la ejecución al cliente
                client_socket.send(result.stdout.encode("utf-8") + result.stderr.encode("utf-8"))
            except Exception as e:
                client_socket.send(f"Error al ejecutar: {str(e)}".encode("utf-8"))

def config_server():
    global client_socket

    # Crear el socket del servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Detectar la IP local automáticamente y asignar un puerto
    ip = socket.gethostbyname(socket.gethostname())
    server_socket.bind((ip, 9090))  # Puedes cambiar 9090 por otro puerto si lo prefieres

    # Esperar conexiones entrantes
    server_socket.listen(1)
    print(f"Servidor iniciado en IP {ip}, puerto 9090. Esperando conexiones...")

    # Aceptar la conexión del cliente
    client_socket, client_address = server_socket.accept()
    print(f"Conexión establecida con {client_address}")

    # Manejar los comandos recibidos del cliente
    handle_commands()

    # Cerrar la conexión
    client_socket.close()

# Configurar y ejecutar el servidor
config_server()
