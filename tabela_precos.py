# Tabela Extra — Preço Unitário por Produto: Real 2025 vs Previsto 2026 (k-NN)

import sys
import io

# Corrige a codificação da consola do Windows (antes dava alguns bugs de formatação)
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import warnings
import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings("ignore")

NAVY  = "#0D1B2A"
RED   = "#C0392B"
FONT  = "Georgia, serif"

# Corre o pipeline REAL do dashboard_final.py
src = open("dashboard_final.py").read()
marker = "interp_p1 ="
idx = src.index(marker)
end = src.index("\n", idx) + 1
exec(src[:end])

# pred_by_prod já contém: Product, qty_2026_bu (Bottom-Up correto), price_2025, price_2026
price_medio_hist = df.groupby("Product")["Price"].mean()

tabela = pred_by_prod[["Product", "price_2025", "price_2026"]].copy()
tabela["price_medio_hist"] = tabela["Product"].map(price_medio_hist)
tabela["variacao_pct"] = (tabela["price_2026"] - tabela["price_2025"]) / tabela["price_2025"] * 100
tabela = tabela[["Product", "price_medio_hist", "price_2025", "price_2026", "variacao_pct"]]

print("Tabela gerada (pipeline real, verificado):")
print(tabela.round(2).to_string(index=False))

# ── Construir a figura Plotly, no estilo do projeto ──
def fmt_eur(v):
    return f"€{v:.2f}"

def fmt_pct(v):
    sinal = "+" if v >= 0 else ""
    return f"{sinal}{v:.1f}%"

header_vals = ["Produto", "Preço médio histórico", "Preço real 2025", "Preço previsto 2026 (k-NN)", "Variação"]
cell_vals = [
    [f"Produto {p}" for p in tabela["Product"]],
    [fmt_eur(v) for v in tabela["price_medio_hist"]],
    [fmt_eur(v) for v in tabela["price_2025"]],
    [fmt_eur(v) for v in tabela["price_2026"]],
    [fmt_pct(v) for v in tabela["variacao_pct"]],
]

font_colors = [RED if v < -20 else NAVY for v in tabela["variacao_pct"]]
font_matrix = [[NAVY]*len(tabela)]*4 + [font_colors]

fig = go.Figure(go.Table(
    columnwidth=[110, 160, 130, 190, 100],
    header=dict(
        values=header_vals,
        fill_color=NAVY,
        font=dict(color="white", size=14, family="Arial Black, Arial, sans-serif"),
        align="center",
        height=38,
    ),
    cells=dict(
        values=cell_vals,
        fill_color=[["#F9F9F9", "white"]*3],
        font=dict(color=font_matrix, size=13, family=FONT),
        align="center",
        height=34,
    )
))

fig.update_layout(
    title=dict(
        text="Preço Unitário por Produto — Real 2025 vs Previsto 2026 (k-NN)",
        font=dict(size=15, color=NAVY, family=FONT),
        x=0.01,
    ),
    margin=dict(t=60, b=30, l=10, r=10),
    height=260,
    paper_bgcolor="white",
)

fig.write_html("tabela_precos_kNN.html", include_plotlyjs="cdn", full_html=True)

time.sleep(1)
fig.write_image("tabela_precos_kNN.png", width=1600, height=400, scale=2)
print()
print("[OK] tabela_precos_kNN.html e tabela_precos_kNN.png gerados")