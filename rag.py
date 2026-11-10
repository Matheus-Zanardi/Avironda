import sys
import chromadb
import ollama
from sentence_transformers import SentenceTransformer

MODELO = "qwen2.5:3b"
K = 3

modelo_emb = SentenceTransformer("BAAI/bge-small-en-v1.5")
colecao = chromadb.PersistentClient(path="chroma_db").get_collection("avironda")


def responder(pergunta):
    q = modelo_emb.encode([pergunta], normalize_embeddings=True).tolist()
    r = colecao.query(query_embeddings=q, n_results=K)

    contexto = ""
    for i, doc in enumerate(r["documents"][0]):
        m = r["metadatas"][0][i]
        contexto += f"[{r['ids'][0][i]}] ({m['fonte']} - {m['titulo']}): {doc}\n"

    prompt = f"""Responda a pergunta usando SOMENTE o contexto abaixo.
Escreva a resposta em uma frase com o valor ou fato pedido, e termine com o id do trecho entre colchetes, por exemplo: "O limite é 20 ppm [emb_002]."
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