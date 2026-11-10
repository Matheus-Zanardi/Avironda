import json
from fastapi import FastAPI
from pydantic import BaseModel
from rag import responder

app = FastAPI(
    title="AviRonda - assistente de ambiente de aviário",
    description="Responde perguntas com base na base de conhecimento, citando a fonte ou recusando quando não consta.",
)


class Pergunta(BaseModel):
    pergunta: str


@app.get("/")
def raiz():
    return {"status": "ok", "docs": "/docs"}


@app.post("/perguntar")
def perguntar(body: Pergunta):
    return json.loads(responder(body.pergunta))