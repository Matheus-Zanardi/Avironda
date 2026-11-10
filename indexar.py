import json
import chromadb
from sentence_transformers import SentenceTransformer

modelo_emb = SentenceTransformer("BAAI/bge-small-en-v1.5")
trechos = [json.loads(l) for l in open("base/trechos.jsonl", encoding="utf-8") if l.strip()]

cliente = chromadb.PersistentClient(path="chroma_db")
colecao = cliente.get_or_create_collection("avironda", metadata={"hnsw:space": "cosine"})

textos = [t["trecho"] for t in trechos]
embeddings = modelo_emb.encode(textos, normalize_embeddings=True).tolist()

colecao.upsert(
    ids=[t["id"] for t in trechos],
    documents=textos,
    embeddings=embeddings,
    metadatas=[{"fonte": t["fonte"], "titulo": t["titulo"], "url": t["url"]} for t in trechos],
)
print(f"{len(trechos)} trechos indexados.")