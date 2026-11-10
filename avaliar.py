import json
from rag import responder

casos = [json.loads(l) for l in open("avaliacao/casos.jsonl", encoding="utf-8") if l.strip()]
resultados = []

for c in casos:
    resposta = responder(c["pergunta"])
    print(f"\n[{c['id']}] {c['pergunta']}\n-> {resposta}")
    resultados.append({
        "id": c["id"],
        "pergunta": c["pergunta"],
        "esperado": c["resposta_esperada"],
        "fonte_esperada": c["fonte_esperada"],
        "resposta": resposta,
    })

with open("resultados/rag.jsonl", "w", encoding="utf-8") as f:
    for x in resultados:
        f.write(json.dumps(x, ensure_ascii=False) + "\n")