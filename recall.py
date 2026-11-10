import json
import chromadb
from sentence_transformers import SentenceTransformer

modelo_emb = SentenceTransformer("BAAI/bge-small-en-v1.5")
colecao = chromadb.PersistentClient(path="chroma_db").get_collection("avironda")

casos = [json.loads(l) for l in open("avaliacao/casos.jsonl", encoding="utf-8") if l.strip()]
casos = [c for c in casos if c["fonte_esperada"]]  # ignora o caso "não consta"

hit1 = hit3 = 0
for c in casos:
    q = modelo_emb.encode([c["pergunta"]], normalize_embeddings=True).tolist()
    r = colecao.query(query_embeddings=q, n_results=3)
    ids = r["ids"][0]
    ok1 = ids[:1] == [c["fonte_esperada"]] or c["fonte_esperada"] in ids[:1]
    ok3 = c["fonte_esperada"] in ids
    hit1 += ok1
    hit3 += ok3
    print(f"{c['id']}  top3={ids}  esperado={c['fonte_esperada']}  r@1={ok1}  r@3={ok3}")

print(f"\nrecall@1 = {hit1}/{len(casos)} = {hit1/len(casos):.2f}")
print(f"recall@3 = {hit3}/{len(casos)} = {hit3/len(casos):.2f}")