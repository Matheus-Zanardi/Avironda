import ollama
from rag import colecao, modelo_emb, MODELO, K


def buscar(texto):
    q = modelo_emb.encode([texto], normalize_embeddings=True).tolist()
    return colecao.query(query_embeddings=q, n_results=K)


def reformular(pergunta):
    prompt = f"""Reescreva a pergunta abaixo como uma busca curta de palavras-chave, em português, em uma única linha, sem explicação.
Pergunta: {pergunta}"""
    r = ollama.chat(model=MODELO, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
    return r["message"]["content"].strip().split("\n")[0]


def coletar(textos):
    vistos, contexto = set(), ""
    for t in textos:
        r = buscar(t)
        for i, id_ in enumerate(r["ids"][0]):
            if id_ in vistos:
                continue
            vistos.add(id_)
            m = r["metadatas"][0][i]
            contexto += f"[{id_}] ({m['fonte']} - {m['titulo']}): {r['documents'][0][i]}\n"
    return contexto


def responder_agente(pergunta):
    busca = reformular(pergunta)
    contexto = coletar([pergunta, busca])

    prompt = f"""Responda a pergunta usando SOMENTE o contexto abaixo.
Se a pergunta citar uma fonte (por exemplo, Embrapa), use apenas os trechos dessa fonte.
Escreva a resposta em uma frase com o valor ou fato pedido, e termine com o id do trecho entre colchetes, por exemplo: "O limite é 20 ppm [emb_002]."
Não cite trechos quando a resposta for "não consta na base".
Se a resposta não estiver no contexto, responda exatamente: "não consta na base".

Contexto:
{contexto}
Pergunta: {pergunta}"""
    r = ollama.chat(model=MODELO, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
    return r["message"]["content"]