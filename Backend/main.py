# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hola_mundo():
    return {"mensaje": "¡Mi API con FastAPI funciona!"}