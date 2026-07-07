# Data Warehouse Vendas — Hierarchical Time Series com Reconciliação Bottom-Up

Projeto Final em Engenharia Informática · Universidade Aberta · Prof. Luís Cavique

**Autores:** Gonçalo Meixieiro · Ulisses Nascimento

---

## Sobre o projeto

Sistema completo de Data Warehouse e Business Intelligence sobre dados reais de vendas
(2021–2025), dividido em duas fases complementares:

- **Fase 2 — Data Warehouse & OLAP**: pipeline ETL, modelo dimensional em estrela
  (F_Vendas + 4 dimensões), e 7 queries OLAP (Roll-Up, Drill-Down, Market Share, YoY,
  Pareto, Pivot, Cubóide).
- **Fase 3 — Forecasting HTS**: previsão hierárquica de quantidade e receita para 2026,
  com o modelo **Max2** (António & Cavique, 2026), validado por backtesting temporal
  contra Moving Average, reconciliação **Bottom-Up**, e estimativa de preço por **k-NN**.

**Resultado principal:** receita total prevista para 2026 de **€6,90M** (+28,4% face a
2025), com o Produto B a tornar-se pela primeira vez o principal motor de receita da
empresa.

## Estrutura do repositório

| Ficheiro | Descrição |
|---|---|
| `Dados_BI_2021_2025.xlsx` | Dataset em bruto (1.604 registos) |
| `limpeza_e_star_schema.py` | Limpeza de dados + construção do modelo dimensional em estrela |
| `dashboard_final.py` | Pipeline completo: OLAP + HTS + backtesting + previsões + dashboard interativo |
| `requirements.txt` | Dependências Python |
| `README_DEMO.md` | Instruções detalhadas de execução para a demonstração |

## Como correr

```bash
pip install -r requirements.txt
python limpeza_e_star_schema.py    # gera dataset_limpo.xlsx + esquema em estrela
python dashboard_final.py          # gera dashboard_final.html com todas as visualizações
```

Ver `README_DEMO.md` para detalhes, outputs esperados, e notas metodológicas.

## Metodologia — destaques

- **Max2**: modelo não-paramétrico para séries temporais curtas e esparsas, validado
  com erro abaixo de 6% em todos os níveis hierárquicos (Região, Produto,
  Cliente×Produto), superando a Moving Average por um fator de 3 a 20 vezes.
- **Reconciliação Bottom-Up**: as previsões são geradas ao nível mais granular
  (Cliente×Produto) e agregadas para cima, garantindo coerência matemática entre todos
  os níveis da hierarquia.
- **k-NN (k=5)**: estimativa exploratória de preço unitário para 2026, combinada com a
  quantidade prevista para produzir a receita projetada.

## Licença

MIT — ver [LICENSE](LICENSE).
