import json
import re


def carregar(caminho):
    linhas = [json.loads(l) for l in open(caminho, encoding="utf-8") if l.strip()]
    return {x["id"]: x for x in linhas}


def obj_resposta(x):
    try:
        obj = json.loads(x["resposta"])
        return obj if isinstance(obj, dict) else None
    except (json.JSONDecodeError, TypeError):
        return None


def texto_resposta(x):
    obj = obj_resposta(x)
    return obj.get("resposta", "") if obj else x["resposta"]


def numeros(t):
    return re.findall(r"\d+", t)


def acerto(x):
    esperado = x["esperado"].lower()
    resp = texto_resposta(x).lower()
    if esperado == "não consta":
        return "não consta" in resp
    if not numeros(esperado):
        return None  # avaliar à mão
    return all(n in numeros(resp) for n in numeros(esperado))


def fonte_ok(x):
    obj = obj_resposta(x)
    return obj is not None and obj.get("fonte") == x["fonte_esperada"]


def json_ok(x):
    obj = obj_resposta(x)
    return obj is not None and "erro" not in obj


base = carregar("resultados/baseline.jsonl")
rag = carregar("resultados/rag.jsonl")
agente = carregar("resultados/agente.jsonl")

print(f"{'caso':<6}{'sem contexto':<14}{'RAG':<8}{'agente':<8}{'fonte RAG':<11}{'JSON RAG':<9}")
totais = {"base": 0, "rag": 0, "agente": 0, "manual": 0, "fonte": 0, "json": 0}
for id_ in base:
    a_base = acerto(base[id_])
    a_rag = acerto(rag[id_])
    a_ag = acerto(agente[id_])
    f = fonte_ok(rag[id_])
    j = json_ok(rag[id_])
    if a_base is None:
        totais["manual"] += 1
    else:
        totais["base"] += a_base
        totais["rag"] += a_rag
        totais["agente"] += a_ag
    totais["fonte"] += f
    totais["json"] += j
    print(f"{id_:<6}{str(a_base):<14}{str(a_rag):<8}{str(a_ag):<8}{str(f):<11}{str(j):<9}")

n = len(base)
print(f"\nSem contexto: {totais['base']}/{n - totais['manual']} acertos automáticos")
print(f"RAG: {totais['rag']}/{n - totais['manual']} acertos automáticos")
print(f"Agente: {totais['agente']}/{n - totais['manual']} acertos automáticos")
print(f"RAG com fonte correta: {totais['fonte']}/{n}")
print(f"RAG com JSON válido: {totais['json']}/{n}")
print(f"Casos para avaliar à mão: {totais['manual']}")