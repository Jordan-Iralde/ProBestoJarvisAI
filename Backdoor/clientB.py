import socket

def send_commands():
    # Recibir el directorio actual del servidor
    current_dir = server_socket.recv(3000).decode("utf-8")
    print(f"Conectado al servidor. Directorio actual: {current_dir}")

    while True:
        # Solicitar el comando al usuario
        command = input(f"{current_dir}-#: ").strip()

        # Enviar el comando al servidor
        server_socket.send(command.encode("utf-8"))

        # Si el comando es "exit", finalizar la conexión
        if command.lower() == "exit":
            print("Cerrando conexión.")
            break

        # Recibir y mostrar el resultado del servidor
        result = server_socket.recv(3000).decode("utf-8")
        print(result)

        # Actualizar el directorio actual si se cambió con "cd"
        if command.startswith("cd"):
            current_dir = result

def config_client():
    global server_socket

    # Crear el socket del cliente
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Conectar al servidor en la IP y puerto correspondientes
    server_ip = input("Introduce la IP del servidor: ").strip()
    server_port = 9090  # Asegúrate de que coincida con el puerto del servidor
    server_socket.connect((server_ip, server_port))

    # Enviar comandos al servidor
    send_commands()

    # Cerrar la conexión
    server_socket.close()

# Configurar y ejecutar el cliente
config_client()
