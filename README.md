# AviRonda: assistente de ambiente de aviário com LLM local (RAG)

Projeto da Global Solution 2026.2 (FIAP, Engenharia de Software 4º ano), componente Inteligência (Generative AI for Engineering).

## Integrantes
| Integrante | RM |
|---|---|
| David Denunci | RM98603 |
| Fernando Popolili | RM99919 |
| Lucas de Toledo | RM97913 |
| Matheus Zanardi | RM98832 |
| Augusto Milreu | RM98245 |

## Problema e solução
Carrinho autônomo que faz ronda em aviário, mede calor e amônia e avisa o granjeiro. A parte de IA é um assistente que responde perguntas sobre ambiente de aviário com base em fontes da Embrapa e do INMET/El Niño, citando a fonte ou recusando quando a informação não consta na base.

## Ficha técnica
- **Cidadão:** produtor avícola.
- **Problema:** calor e amônia em aviários podem prejudicar a saúde das aves e o desempenho.
- **Componentes de IA:** LLM local (qwen2.5:3b via Ollama), embeddings (BAAI/bge-small-en-v1.5), ChromaDB.
- **Fontes:** Embrapa (amônia, estresse calórico, ventilação), aviNews e Exame Agro (El Niño).
- **ODS:** 2 (fome zero e agricultura sustentável), 3 (saúde e bem-estar), 9 (indústria, inovação e infraestrutura).

## Como reproduzir
1. Instale [Python 3.10+](https://www.python.org/) e o [Ollama](https://ollama.com/download).
2. Baixe o modelo: `ollama pull qwen2.5:3b`
3. Crie o ambiente:

python -m venv .venv
.venv\Scripts\activate
pip install ollama chromadb sentence-transformers pandas

4. Indexe a base: `python indexar.py`
5. Teste uma pergunta: `python rag.py "Qual o limite de amônia recomendado para exportadores de frango?"`

## Avaliação
- `baseline.py`: respostas da LLM sem contexto.
- `avaliar.py`: respostas com RAG.
- `avaliar_agente.py`: respostas com agente (reformula a pergunta e faz duas buscas).
- `placar.py`: compara as três configurações.

Casos de teste em `avaliacao/casos.jsonl`, inclusive um caso com resposta "não consta".

## Resultados (11 casos)
| Configuração | Acertos automáticos (10 casos) |
|---|---|
| Sem contexto | 1 |
| RAG simples | 9 |
| Agente | 9 |

O caso c05 (efeitos do El Niño) é avaliado à mão.

## Erros encontrados
1. **Sem contexto (c01):** não conhece o limite de 20 ppm. Correção: RAG com a base.
2. **Sem contexto (c02):** inventa valores (20 e 10 ppm) e atribui à Embrapa. Correção: responder só com a base.
3. **Sem contexto (c04):** inventa limite de CO2 (10%). Correção: recusa "não consta na base".
4. **RAG, versão 1 (c06):** usou 20 ppm dos exportadores no lugar de 25 ppm da Embrapa. Correção: usar a fonte citada na pergunta.
5. **RAG, versão 2 (c03):** resposta incompleta (36 ppm em vez dos 3 valores). Correção proposta: listar todos os valores pedidos.

## Limitações
- Modelo de 3B parâmetros, rodando em GPU de 6 GB.
- Base pequena (16 trechos).
- Parte do El Niño vem de notícias do setor, não do Painel El Niño oficial.
- O agente não superou o RAG simples nesse conjunto.