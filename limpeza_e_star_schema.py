"""
Fase 2 — Limpeza de Dados e Construção do Modelo em Estrela
Data Warehouse Vendas — Demonstração para a defesa (10/07/2026)

Entrada:  Dados_BI_2021_2025.xlsx (dados em bruto)
Saída:    dataset_limpo.xlsx (dataset tratado)
          F_Vendas.xlsx, D_Tempo.xlsx, D_Regiao.xlsx, D_Produto.xlsx, D_Cliente.xlsx (esquema em estrela)
"""

import pandas as pd

RAW = "Dados_BI_2021_2025.xlsx"

print("=" * 30)
print("  LIMPEZA DE DADOS + CONSTRUÇÃO DO MODELO EM ESTRELA")
print("=" * 30)

# BLOCO 1: CARREGAR E LIMPAR OS DADOS EM BRUTO

print("\n[1/3] Carregar e limpar os dados em bruto...")

df = pd.read_excel(RAW)
df.columns = df.columns.str.strip()          # remover espaços extra nos nomes das colunas
n_original = len(df)

# Remover espaços extra e uniformizar maiúsculas
df["Region"]  = df["Region"].astype(str).str.strip().str.upper()
df["Product"] = df["Product"].astype(str).str.strip().str.upper()
df["Year"]    = df["Year"].astype(int)

# Regra 1 — remover registos com preço inválido (negativo ou zero)
erros = df[df["Price"] <= 0]
df = df[df["Price"] > 0]

# Regra 2 — remover devoluções (quantidade negativa)
devolucoes = df[df["Qty"] < 0]
df = df[df["Qty"] >= 0]

# Regra 3 — verificar anos válidos (2021–2025)
fora_do_periodo = df[~df["Year"].between(2021, 2025)]
df = df[df["Year"].between(2021, 2025)]

# Regra 4 — eliminar duplicados exatos
n_antes_dedup = len(df)
df = df.drop_duplicates()
n_duplicados = n_antes_dedup - len(df)

# Calcular Valor_Total
df["Valor_Total"] = (df["Price"] * df["Qty"]).round(2)
df = df.reset_index(drop=True)

print(f"      Registos originais:        {n_original}")
print(f"      Removidos (preço inválido): {len(erros)}")
print(f"      Removidos (devoluções):     {len(devolucoes)}")
print(f"      Removidos (fora do período):{len(fora_do_periodo)}")
print(f"      Removidos (duplicados):     {n_duplicados}")
print(f"      Registos válidos finais:    {len(df)}")

df.to_excel("dataset_limpo.xlsx", index=False)
print("      [OK] dataset_limpo.xlsx gerado")

# BLOCO 2: CONSTRUÇÃO DO MODELO DIMENSIONAL EM ESTRELA

print("\n[2/3] Construir o modelo dimensional em estrela...")

# D_Tempo
D_Tempo = pd.DataFrame({"Year": sorted(df["Year"].unique())})
D_Tempo.insert(0, "id_tempo", range(1, len(D_Tempo) + 1))

# D_Regiao
D_Regiao = pd.DataFrame({"Region": sorted(df["Region"].unique())})
D_Regiao.insert(0, "id_regiao", range(1, len(D_Regiao) + 1))

# D_Produto
D_Produto = pd.DataFrame({"Product": sorted(df["Product"].unique())})
D_Produto.insert(0, "id_produto", range(1, len(D_Produto) + 1))

# D_Cliente
D_Cliente = pd.DataFrame({"Client": sorted(df["Client"].unique())})
D_Cliente.insert(0, "id_cliente", range(1, len(D_Cliente) + 1))

print(f"      D_Tempo:   {len(D_Tempo)} linhas")
print(f"      D_Regiao:  {len(D_Regiao)} linhas")
print(f"      D_Produto: {len(D_Produto)} linhas")
print(f"      D_Cliente: {len(D_Cliente)} linhas ({df['Client'].nunique()} clientes únicos)")

# F_Vendas — juntar as chaves estrangeiras / foreign keys
F_Vendas = df.merge(D_Tempo,   on="Year") \
             .merge(D_Regiao,  on="Region") \
             .merge(D_Produto, on="Product") \
             .merge(D_Cliente, on="Client")

F_Vendas = F_Vendas[["id_tempo", "id_regiao", "id_produto", "id_cliente", "Qty", "Price", "Valor_Total"]]
F_Vendas.insert(0, "id_venda", range(1, len(F_Vendas) + 1))

print(f"      F_Vendas:  {len(F_Vendas)} linhas (tabela de factos)")

# BLOCO 3: EXPORTAR O ESQUEMA EM ESTRELA

print("\n[3/3] Exportar as tabelas do esquema em estrela...")

F_Vendas.to_excel("F_Vendas.xlsx", index=False)
D_Tempo.to_excel("D_Tempo.xlsx", index=False)
D_Regiao.to_excel("D_Regiao.xlsx", index=False)
D_Produto.to_excel("D_Produto.xlsx", index=False)
D_Cliente.to_excel("D_Cliente.xlsx", index=False)

print("      [OK] F_Vendas.xlsx, D_Tempo.xlsx, D_Regiao.xlsx, D_Produto.xlsx, D_Cliente.xlsx gerados")
print("\nConcluído — modelo dimensional em estrela pronto para as queries OLAP a serem corridas.")