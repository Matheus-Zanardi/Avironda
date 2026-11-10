import json
import chromadb
from sentence_transformers import SentenceTransformer

modelo_emb = SentenceTransformer("BAAI/bge-small-en-v1.5")
colecao = chromadb.PersistentClient(path="chroma_db").get_collection("avironda")

casos = [json.loads(l) for l in open("avaliacao/casos.jsonl", encoding="utf-8") if l.strip()]

for c in casos:
    q = modelo_emb.encode([c["pergunta"]], normalize_embeddings=True).tolist()
    r = colecao.query(query_embeddings=q, n_results=1)
    d = r["distances"][0][0]
    esperado = c["fonte_esperada"] or "não consta"
    print(f"{c['id']}  dist={d:.3f}  top1={r['ids'][0][0]}  esperado={esperado}")