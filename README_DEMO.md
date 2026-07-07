# Demonstração — Data Warehouse Vendas (Defesa 10/07/2026)

## Ficheiros neste presente pacote

1. `Dados_BI_2021_2025.xlsx` — dataset em bruto (1.604 registos).
2. `limpeza_e_star_schema.py` — limpeza dos dados + construção do modelo dimensional em estrela (F_Vendas + 4 dimensões).
3. `dashboard_final.py` — script único e autocontido: Fase 2 (OLAP: Q01,Q02,Q04-Q08) + Fase 3 (backtesting Max2 vs Moving Average, P1, P2, Waterfall, RP1, RP2, Tabela Analítica). Já inclui a correção da reconciliação de receita por Região×Produto.
4. `requirements.txt` — dependências Python necessárias.

O código real mostra:
```
Registos originais:        1604
Removidos (preço inválido): 4
Removidos (devoluções):     4
Registos válidos finais:    1596

pip install -r requirements.txt          # fazer ANTES do dia
python limpeza_e_star_schema.py          # Fase 2 — limpeza + esquema em estrela
python dashboard_final.py                # Fase 2 (queries OLAP) + Fase 3 (HTS, backtesting, previsões)
```

### Output esperado a partir do 1º script (limpeza + estrela)
```
Registos originais:        1604
Removidos (preço inválido): 4
Removidos (devoluções):     4
Registos válidos finais:    1596
D_Tempo:   5 linhas
D_Regiao:  5 linhas
D_Produto: 4 linhas
D_Cliente: 667 linhas (667 clientes únicos)
F_Vendas:  1596 linhas (tabela de factos)
```

### Output esperado do 2º script (dashboard completo)
```
Carregar dados...
A calcular previsões HTS...
  Revenue 2025: €5,375,091 → 2026: €6,900,113 (+28.4%)
A gerar HTML...
[OK] dashboard_final.html
```

Depois de correr o 2º script, abrir o `dashboard_final.html` no browser para mostrar as 15 visualizações + tabela.


