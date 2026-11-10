import json
import re


def carregar(caminho):
    linhas = [json.loads(l) for l in open(caminho, encoding="utf-8") if l.strip()]
    return {x["id"]: x for x in linhas}


def numeros(texto):
    return re.findall(r"\d+", texto)


def acerto(x):
    esperado = x["esperado"].lower()
    resposta = x["resposta"].lower()
    if esperado == "não consta":
        return "não consta" in resposta
    if not numeros(esperado):
        return None  # avaliar à mão
    return all(n in numeros(resposta) for n in numeros(esperado))


base = carregar("resultados/baseline.jsonl")
rag = carregar("resultados/rag.jsonl")
agente = carregar("resultados/agente.jsonl")

print(f"{'caso':<6}{'sem contexto':<16}{'RAG':<10}{'agente':<10}")
totais = {"base": 0, "rag": 0, "agente": 0, "manual": 0}
for id_ in base:
    a_base = acerto(base[id_])
    a_rag = acerto(rag[id_])
    a_ag = acerto(agente[id_])
    if a_base is None:
        totais["manual"] += 1
    else:
        totais["base"] += a_base
        totais["rag"] += a_rag
        totais["agente"] += a_ag
    print(f"{id_:<6}{str(a_base):<16}{str(a_rag):<10}{str(a_ag):<10}")

print(f"\nSem contexto: {totais['base']} acertos automáticos")
print(f"RAG: {totais['rag']} acertos automáticos")
print(f"Agente: {totais['agente']} acertos automáticos")
print(f"Casos para avaliar à mão: {totais['manual']}")