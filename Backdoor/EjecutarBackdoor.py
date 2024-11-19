import subprocess

def ejecutar_programa(ruta_programa, *argumentos):
    """
    Ejecuta un programa externo y captura su salida.
    
    :param ruta_programa: Ruta del programa o comando a ejecutar.
    :param argumentos: Argumentos adicionales para el programa.
    :return: Código de salida y salida estándar/error del programa.
    """
    try:
        # Ejecutar el programa con los argumentos
        resultado = subprocess.run(
            [ruta_programa, *argumentos],
            text=True,
            capture_output=True,
            check=True
        )
        print("Salida estándar:")
        print(resultado.stdout)
        return resultado.returncode, resultado.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando {ruta_programa}:")
        print(e.stderr)
        return e.returncode, e.stderr
    except FileNotFoundError:
        print(f"El programa {ruta_programa} no se encontró.")
        return -1, "Archivo no encontrado."

# Ejemplo de uso
if __name__ == "__main__":
    programa = input("Ingresa el programa/comando a ejecutar: ")
    argumentos = input("Ingresa los argumentos separados por espacios: ").split()
    codigo, salida = ejecutar_programa(programa, *argumentos)
    print(f"Código de salida: {codigo}")
