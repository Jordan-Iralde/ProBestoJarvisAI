from fastapi import FastAPI
from core.engine import procesar_comando

app = FastAPI()

@app.post("/comando")
def comando_api(entrada: str):
    return {"respuesta": procesar_comando(entrada)}
