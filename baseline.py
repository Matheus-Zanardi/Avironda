import json
import ollama

MODELO = "qwen2.5:3b"

casos = [json.loads(l) for l in open("avaliacao/casos.jsonl", encoding="utf-8") if l.strip()]
resultados = []

for c in casos:
    r = ollama.chat(
        model=MODELO,
        messages=[{"role": "user", "content": c["pergunta"]}],
        options={"temperature": 0},
    )
    resposta = r["message"]["content"]
    resultados.append({"id": c["id"], "pergunta": c["pergunta"], "esperado": c["resposta_esperada"], "resposta": resposta})
    print(f"\n[{c['id']}] {c['pergunta']}\n-> {resposta}")

import os
os.makedirs("resultados", exist_ok=True)
with open("resultados/baseline.jsonl", "w", encoding="utf-8") as f:
    for x in resultados:
        f.write(json.dumps(x, ensure_ascii=False) + "\n")