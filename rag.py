import sys
import chromadb
import ollama
from sentence_transformers import SentenceTransformer

MODELO = "qwen2.5:3b"
K = 3
LIMIAR = 0.20  # distância máxima do melhor trecho; acima disso, recusa sem chamar a LLM

modelo_emb = SentenceTransformer("BAAI/bge-small-en-v1.5")
colecao = chromadb.PersistentClient(path="chroma_db").get_collection("avironda")


def responder(pergunta):
    q = modelo_emb.encode([pergunta], normalize_embeddings=True).tolist()
    r = colecao.query(query_embeddings=q, n_results=K)

    if r["distances"][0][0] > LIMIAR:
        return "não consta na base"

    contexto = ""
    for i, doc in enumerate(r["documents"][0]):
        m = r["metadatas"][0][i]
        contexto += f"[{r['ids'][0][i]}] ({m['fonte']} - {m['titulo']}): {doc}\n"

    prompt = f"""Responda a pergunta usando SOMENTE o contexto abaixo.
Se a pergunta citar uma fonte (por exemplo, Embrapa), use apenas os trechos dessa fonte.
Escreva a resposta em uma frase com o valor ou fato pedido, e termine com o id do trecho entre colchetes, por exemplo: "O limite é 20 ppm [emb_002]."
Não cite trechos quando a resposta for "não consta na base".
Se a resposta não estiver no contexto, responda exatamente: "não consta na base".

Contexto:
{contexto}
Pergunta: {pergunta}"""

    resp = ollama.chat(
        model=MODELO,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )
    return resp["message"]["content"]


if __name__ == "__main__":
    pergunta = " ".join(sys.argv[1:]) or input("Pergunta: ")
    print(responder(pergunta))