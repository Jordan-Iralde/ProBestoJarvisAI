@echo off
:: Verificar si Python está instalado
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python no está instalado en este sistema. Por favor, instala Python y vuelve a intentarlo.
    pause
    exit /b
)

:: Ejecutar el script Python
python -c "import socket; \
def send_commands(): \
    current_dir = server_socket.recv(3000).decode('utf-8'); \
    print(f'Conectado al servidor. Directorio actual: {current_dir}'); \
    while True: \
        command = input(f'{current_dir}-#: ').strip(); \
        server_socket.send(command.encode('utf-8')); \
        if command.lower() == 'exit': \
            print('Cerrando conexión.'); \
            break; \
        result = server_socket.recv(3000).decode('utf-8'); \
        print(result); \
        if command.startswith('cd'): \
            current_dir = result; \
def config_client(): \
    global server_socket; \
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM); \
    server_ip = input('Introduce la IP del servidor: ').strip(); \
    server_port = 9090; \
    server_socket.connect((server_ip, server_port)); \
    send_commands(); \
    server_socket.close(); \
config_client()"

:: Fin del script
pause
