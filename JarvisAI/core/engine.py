from core.dispatcher import ejecutar_comando


def procesar_comando(texto_usuario: str) -> str:
    """Procesa el texto del usuario y devuelve una respuesta."""
    if not texto_usuario:
        return "No escuché nada."

    respuesta = ejecutar_comando(texto_usuario.lower().strip())

    if respuesta:
        return respuesta
    else:
        return "No entendí el comando. ¿Podés repetirlo?"
