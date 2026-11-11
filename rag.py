import sys
import json
import chromadb
import ollama
from sentence_transformers import SentenceTransformer

MODELO = "qwen2.5:3b"
K = 3
LIMIAR = 0.20  # distância máxima do melhor trecho; acima disso, recusa sem chamar a LLM

modelo_emb = SentenceTransformer("BAAI/bge-small-en-v1.5")
colecao = chromadb.PersistentClient(path="chroma_db").get_collection("avironda")


def recusa():
    return json.dumps({"resposta": "não consta na base", "fonte": None, "encontrou": False}, ensure_ascii=False)


def extrair_json(texto):
    inicio, fim = texto.find("{"), texto.rfind("}")
    if inicio == -1 or fim == -1:
        return None
    try:
        return json.loads(texto[inicio:fim + 1])
    except json.JSONDecodeError:
        return None


def responder(pergunta):
    q = modelo_emb.encode([pergunta], normalize_embeddings=True).tolist()
    r = colecao.query(query_embeddings=q, n_results=K)

    if r["distances"][0][0] > LIMIAR:
        return recusa()

    ids = r["ids"][0]
    contexto = ""
    for i, doc in enumerate(r["documents"][0]):
        m = r["metadatas"][0][i]
        contexto += f"[{ids[i]}] ({m['fonte']} - {m['titulo']}): {doc}\n"

    prompt = f"""Responda a pergunta usando SOMENTE o contexto abaixo.
Se a pergunta citar uma fonte (por exemplo, Embrapa), use apenas os trechos dessa fonte.
Responda APENAS com um objeto JSON, sem texto antes ou depois, neste formato:
{{"resposta": "frase com o valor ou fato pedido", "fonte": "id do trecho usado", "encontrou": true}}
Se a resposta não estiver no contexto, responda exatamente:
{{"resposta": "não consta na base", "fonte": null, "encontrou": false}}

Contexto:
{contexto}
Pergunta: {pergunta}"""

    resp = ollama.chat(
        model=MODELO,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )
    obj = extrair_json(resp["message"]["content"])

    if obj is None or "resposta" not in obj or "encontrou" not in obj:
        return json.dumps({"resposta": resp["message"]["content"], "fonte": None, "encontrou": None, "erro": "JSON inválido"}, ensure_ascii=False)

    if obj["fonte"] not in ids:
        obj["fonte"] = None
    return json.dumps(obj, ensure_ascii=False)


if __name__ == "__main__":
    pergunta = " ".join(sys.argv[1:]) or input("Pergunta: ")
    print(responder(pergunta))