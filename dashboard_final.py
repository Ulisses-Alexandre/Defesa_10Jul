"""
Dashboard Unificado
14 visualizações + 1 tabela analítica
"""

import warnings, os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import LabelEncoder
warnings.filterwarnings("ignore")

RAW  = "dataset_limpo.xlsx"
OUT  = "dashboard_final.html"

PA = "#F26C64"   # Produto A — coral
PB = "#7CAE00"   # Produto B — verde
PC = "#4DB7C5"   # Produto C — turquesa
PD = "#B07AD9"   # Produto D — roxo
PROD_C = {"A": PA, "B": PB, "C": PC, "D": PD}

RA = "#C0392B"   # Região A — vermelho
RB = "#E68613"   # Região B — laranja
RC = "#4C93C3"   # Região C — azul
RD = "#3B7F49"   # Região D — verde
RE = "#8E44AD"   # Região E — roxo
REG_C = {"A": RA, "B": RB, "C": RC, "D": RD, "E": RE}

NAVY  = "#0D1B2A"
GREEN = "#1E8449"
RED   = "#C0392B"
AMBER = "#D68910"
FONT  = "Georgia, serif"

# ── Layout base
def bl(title, h=400):
    return dict(
        title=dict(text=title, font=dict(size=13, color=NAVY, family=FONT)),
        height=h, plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family=FONT, color="#1C2833", size=11),
        margin=dict(t=55, b=45, l=55, r=25),
        legend=dict(bgcolor="rgba(255,255,255,0.95)", bordercolor="#D5D8DC", borderwidth=1),
    )

def to_div(fig):
    return fig.to_html(full_html=False, include_plotlyjs=False,
                       config={"responsive": True, "displayModeBar": False})

print("A carregar dados...")
df = pd.read_excel(RAW)
df.columns = df.columns.str.strip()
YEARS = sorted(df["Year"].unique().tolist())
PRODUTOS = sorted(df["Product"].unique().tolist())
REGIOES = sorted(df["Region"].unique().tolist())


# FASE 2 — OLAP


# ── Q01 Roll-Up
q01 = df.groupby("Year")["Valor_Total"].sum().reset_index().sort_values("Year")
_q01_anos  = q01["Year"].astype(str).tolist()
_q01_vals  = (q01["Valor_Total"] / 1e6).tolist()
_q01_cores = [NAVY if y < 2025 else AMBER for y in q01["Year"]]
_q01_txt   = [f"€{v:.2f}M" for v in _q01_vals]
fig_q01 = go.Figure(go.Bar(
    x=_q01_anos, y=_q01_vals,
    marker_color=_q01_cores,
    text=_q01_txt, textposition="outside",
    textfont=dict(size=14, family=FONT, color=NAVY),
    width=0.4,
    hovertemplate="<b>%{x}</b><br>\u20ac%{y:.2f}M<extra></extra>",
))
fig_q01.update_layout(**bl("Q01 \u2014 Roll-Up: Vendas Totais por Ano"))
fig_q01.update_xaxes(showgrid=False, title="Ano", tickfont=dict(size=13), title_font=dict(size=13))
fig_q01.update_yaxes(
    title="Vendas totais (\u20acM)", gridcolor="#EAECEE",
    tickformat=".2f", ticksuffix="M",
    tickfont=dict(size=13), title_font=dict(size=13),
    range=[0, max(_q01_vals) * 1.18],
)
interp_q01 = "As vendas cresceram consistentemente entre 2021 e 2024 (+70.7% acumulado), registando uma ligeira quebra em 2025 (-4.0%). Este comportamento pode indicar desaceleração ou possível saturação de mercado, justificando a análise preditiva desenvolvida na Fase 3."

# ── Q02 Drill-Down
q02 = df.groupby(["Year","Region"])["Valor_Total"].sum().reset_index().sort_values("Year")
_anos_q02 = ["2021","2022","2023","2024","2025"]
fig_q02 = go.Figure()
for reg in REGIOES:
    sub = q02[q02["Region"]==reg].sort_values("Year")
    _vals = [(sub[sub["Year"]==int(a)]["Valor_Total"].values[0]/1e6
              if int(a) in sub["Year"].values else 0) for a in _anos_q02]
    fig_q02.add_trace(go.Bar(
        name=f"Região {reg}",
        x=_anos_q02,
        y=_vals,
        marker_color=REG_C[reg],
        hovertemplate=f"<b>Região {reg}</b> — %{{x}}<br>€%{{y:.2f}}M<extra></extra>",
    ))
fig_q02.update_layout(**bl("Q02 — Drill-Down: Vendas por Ano e Região", h=440),
    barmode="stack",
    xaxis=dict(type="category", categoryorder="array", categoryarray=_anos_q02))
fig_q02.update_xaxes(showgrid=False, title="Ano")
fig_q02.update_yaxes(title="Vendas totais (€M)", gridcolor="#EAECEE",
    tickformat=".2f", ticksuffix="M")
interp_q02 = "A Região A domina consistentemente a estrutura de vendas, representando cerca de 67% do total. A Região B apresenta o maior crescimento relativo entre 2021 e 2025 (+207%), enquanto as Regiões D e E evidenciam perda de peso após 2023."

# ── Q04 Market Share
q04 = df.groupby(["Year","Region"])["Valor_Total"].sum().reset_index()
q04["total_ano"] = q04.groupby("Year")["Valor_Total"].transform("sum")
q04["quota_pct"] = (q04["Valor_Total"] / q04["total_ano"] * 100).round(1)
fig_q04 = go.Figure()
for reg in REGIOES:
    sub = q04[q04["Region"]==reg].sort_values("Year")
    _anos = sub["Year"].astype(str).tolist()
    _quotas = sub["quota_pct"].tolist()
    _txt = [f"{v:.1f}%" if str(y) == "2025" else "" for v, y in zip(_quotas, sub["Year"])]
    fig_q04.add_trace(go.Scatter(
        name=f"Região {reg}",
        x=_anos, y=_quotas,
        mode="lines+markers+text",
        text=_txt, textposition="top center",
        line=dict(color=REG_C[reg], width=2.5),
        marker=dict(size=8),
        hovertemplate=f"<b>Região {reg}</b> — %{{x}}<br>%{{y:.1f}}%<extra></extra>",
    ))
fig_q04.update_layout(**bl("Q04 — Market Share: Quota % por Região e Ano", h=440))
fig_q04.update_xaxes(showgrid=False, title="Ano", type="category",
    categoryorder="array", categoryarray=["2021","2022","2023","2024","2025"])
fig_q04.update_yaxes(title="Quota de mercado (%)", gridcolor="#EAECEE",
    ticksuffix="%", range=[0, 80])
interp_q04 = "A Região A mantém uma posição dominante e relativamente estável, representando cerca de 67% das vendas. A Região B apresenta o maior ganho de quota, subindo de 7.8% para 14.7%, enquanto a Região E regista a maior perda estrutural no período."

# ── Q05 YoY Growth
q05 = df.groupby("Year")["Valor_Total"].sum().reset_index().sort_values("Year")
q05["yoy"] = q05["Valor_Total"].pct_change() * 100
_q05_anos = q05["Year"].astype(str).tolist()
_q05_vals = (q05["Valor_Total"] / 1e6).tolist()
_q05_yoy  = q05["yoy"].tolist()
fig_q05 = go.Figure()
fig_q05.add_trace(go.Bar(
    x=_q05_anos, y=_q05_vals,
    name="Vendas Totais (€M)",
    marker_color=["#1B4F8A" if a != "2025" else AMBER for a in _q05_anos],
    text=[f"€{v:.2f}M" for v in _q05_vals], textposition="outside",
    yaxis="y", hovertemplate="<b>%{x}</b><br>€%{y:.2f}M<extra></extra>",
))
fig_q05.add_trace(go.Scatter(
    x=_q05_anos[1:], y=_q05_yoy[1:],
    name="Crescimento YoY (%)", mode="lines+markers+text",
    text=[f"{v:+.1f}%" for v in _q05_yoy[1:]],
    textposition=["top center" if v >= 0 else "bottom center" for v in _q05_yoy[1:]],
    textfont=dict(size=11, color=NAVY, family=FONT),
    line=dict(color="#2E7D32", width=2.5),
    marker=dict(size=9, color=["#B03A2E" if v < 0 else "#2E7D32" for v in _q05_yoy[1:]]),
    yaxis="y2", hovertemplate="<b>%{x}</b><br>YoY: %{y:+.1f}%<extra></extra>",
))
fig_q05.update_layout(
    **bl("Q05 — Crescimento Anual de Vendas (YoY)", h=460),
    xaxis=dict(type="category", categoryorder="array",
               categoryarray=_q05_anos, showgrid=False, title="Ano"),
    yaxis=dict(title="Vendas totais (€M)", tickformat=".2f", ticksuffix="M",
               gridcolor="#EAECEE"),
    yaxis2=dict(title="Crescimento YoY (%)", overlaying="y", side="right",
                showgrid=False, zeroline=True, zerolinecolor="#95A5A6",
                zerolinewidth=1.5, ticksuffix="%", range=[-10, 55]),
)
interp_q05 = "O maior crescimento ocorreu em 2022 (+49.1%), seguido de uma desaceleração progressiva em 2023 (+8.4%) e 2024 (+5.6%). Em 2025, a taxa torna-se negativa (-4.0%), sinalizando a primeira contração do período analisado e reforçando a necessidade de uma abordagem preditiva na Fase 3."

# ── Q06 Pareto
q06_all = df.groupby("Client")["Valor_Total"].sum().reset_index()
_total_global = q06_all["Valor_Total"].sum()
q06 = q06_all.sort_values("Valor_Total", ascending=False).head(30).reset_index(drop=True)
q06["acum_pct"] = q06["Valor_Total"].cumsum() / _total_global * 100
q06["rank"] = [f"#{i+1} · {c}" for i, c in enumerate(q06["Client"])]
_x = [str(i) for i in range(30)]
_y_bar = (q06["Valor_Total"]/1e6).round(3).tolist()
_y_acum = q06["acum_pct"].round(1).tolist()
_labels = q06["Client"].astype(str).tolist()
_ranks = q06["rank"].tolist()
fig_q06 = go.Figure()
fig_q06.add_trace(go.Bar(
    x=_x,
    y=_y_bar,
    name="Receita por cliente (€M)",
    marker_color=NAVY,
    customdata=_ranks,
    hovertemplate="<b>%{customdata}</b><br>€%{y:.2f}M<extra></extra>",
))
fig_q06.add_trace(go.Scatter(
    x=_x,
    y=_y_acum,
    name="Acumulado %", mode="lines+markers",
    line=dict(color=AMBER, width=2), marker=dict(size=6),
    yaxis="y2",
    customdata=_ranks,
    hovertemplate="<b>%{customdata}</b><br>Acumulado: %{y:.1f}%<extra></extra>",
))
fig_q06.add_hline(
    y=80, line_dash="dash", line_color=RED, line_width=1.5,
    annotation_text="  Meta Pareto 80%",
    annotation_position="top left",
    annotation_font=dict(color=RED, size=10),
    yref="y2"
)
fig_q06.update_layout(
    **bl("Q06 — Pareto 80/20: Segmentação de Clientes (Top 30)", h=460),
    yaxis=dict(title="Receita individual por cliente (€M)", tickformat=".2f",
               ticksuffix="M", gridcolor="#EAECEE"),
    yaxis2=dict(title="Acumulado (%)", overlaying="y", side="right",
                showgrid=False, ticksuffix="%", range=[0, 105]),
    xaxis=dict(
        showgrid=False, title="Cliente (ordenado por receita decrescente)",
        tickmode="array",
        tickvals=_x,
        ticktext=_labels,
        tickangle=45,
    ),
)
fig_q06.update_layout(margin=dict(t=55, b=45, l=55, r=90))
fig_q06.update_layout(legend=dict(x=0.01, y=0.99, xanchor="left", yanchor="top"))
interp_q06 = "O maior cliente representa 10.2% da faturação total. Os 30 maiores clientes acumulam 61% da receita, todos classificados como Tier A, indicando uma base relevante de clientes estratégicos, mas sem concentração excessiva num único cliente."

# ── Q07 Pivot Produto×Ano
q07 = df.groupby(["Year","Product"])["Valor_Total"].sum().reset_index()
_anos_q07 = ["2021","2022","2023","2024","2025"]
fig_q07 = go.Figure()
for prod in PRODUTOS:
    sub = q07[q07["Product"]==prod].sort_values("Year")
    _vals = [(sub[sub["Year"]==int(a)]["Valor_Total"].values[0]/1e6
              if int(a) in sub["Year"].values else 0) for a in _anos_q07]
    _txt = []
    for v, a in zip(_vals, _anos_q07):
        if a == "2025":
            if v >= 0.3:
                _txt.append(f"€{v:.2f}M")
            else:
                _txt.append(f"€{round(v*1000):.0f}k")
        else:
            _txt.append("")
    fig_q07.add_trace(go.Bar(
        name=f"Produto {prod}",
        x=_anos_q07, y=_vals,
        marker_color=PROD_C[prod],
        text=_txt, textposition="outside",
        hovertemplate=f"<b>Produto {prod}</b> — %{{x}}<br>€%{{y:.2f}}M<extra></extra>",
    ))
fig_q07.update_layout(**bl("Q07 — Receita por Produto e Ano", h=460),
    barmode="group",
    xaxis=dict(type="category", categoryorder="array",
               categoryarray=_anos_q07, showgrid=False, title="Ano"),
)
fig_q07.update_yaxes(title="Receita total (€M)", gridcolor="#EAECEE",
    tickformat=".2f", ticksuffix="M")
interp_q07 = "O Produto A lidera a receita ao longo do período, mas regista uma quebra em 2025 (-9.8%). O Produto B recupera em 2025 (+6.8%), enquanto os Produtos C e D apresentam declínio contínuo desde 2022."

# ── Q08 Cuboide Ano×Região×Produto
from plotly.subplots import make_subplots
q08 = df.groupby(["Year","Region","Product"])["Valor_Total"].sum().reset_index()
_anos_q08 = [2021, 2022, 2023, 2024, 2025]
fig_q08 = make_subplots(
    rows=1, cols=5,
    subplot_titles=[str(a) for a in _anos_q08],
    shared_yaxes=True,
)
for col_i, ano in enumerate(_anos_q08):
    sub = q08[q08["Year"]==ano]
    matrix = []
    for reg in sorted(REGIOES, reverse=True):  # E→A, heatmap inverte → RA no topo
        row_vals = []
        for prod in sorted(PRODUTOS):
            val = sub[(sub["Region"]==reg) & (sub["Product"]==prod)]["Valor_Total"].values
            row_vals.append(round(val[0]/1e3, 1) if len(val)>0 else 0)
        matrix.append(row_vals)
    fig_q08.add_trace(go.Heatmap(
        z=matrix,
        x=[f"P{p}" for p in sorted(PRODUTOS)],
        y=[f"R{r}" for r in sorted(REGIOES, reverse=True)],
        colorscale=[[0,"#F7F9FB"],[0.3,"#AED6F1"],[0.7,"#2E86C1"],[1,"#0D1B2A"]],
        showscale=(col_i == 4),
        colorbar=dict(title="Receita (€k)", x=1.02),
        zmin=0, zmax=q08["Valor_Total"].max()/1e3,
        hovertemplate="<b>%{y} × %{x}</b><br>€%{z:.0f}k<extra></extra>",
        text=[[f"€{v:.0f}k" if v>0 else "—" for v in row] for row in matrix],
        texttemplate="%{text}",
        textfont=dict(size=8, family=FONT),
    ), row=1, col=col_i+1)
fig_q08.update_layout(
    **bl("Q08 — Cuboide OLAP: Ano × Região × Produto", h=380),
)
fig_q08.update_xaxes(showgrid=False)
fig_q08.update_yaxes(showgrid=False)
interp_q08 = "O cuboide Tempo×Região×Produto permite identificar a distribuição da receita por produto dentro de cada região e ano. A análise confirma a dominância dos Produtos A e B, sobretudo na Região A, e evidencia a quebra de 2025 como transversal ao portefólio, embora com maior impacto absoluto nos produtos de maior receita."

# FASE 3 — HTS

print("A calcular previsões HTS...")

YEAR_PRED = 2026
ALPHA = 0.05
YEARS_ALL = [2021, 2022, 2023, 2024, 2025]

df["prod_enc"] = LabelEncoder().fit_transform(df["Product"])
df["reg_enc"]  = LabelEncoder().fit_transform(df["Region"])

def make_wide(df_in, group_cols, val_col):
    piv = df_in.pivot_table(index=group_cols, columns="Year", values=val_col, aggfunc="sum").reset_index()
    piv.columns.name = None
    for y in YEARS_ALL:
        if y not in piv.columns: piv[y] = np.nan
    return piv

wide_prod = make_wide(df, ["Product"], "Qty")
wide_cli  = make_wide(df, ["Client","Product"], "Qty")

def max2(row, yr_list):
    vals = [row[y] for y in yr_list if y in row.index and pd.notna(row[y]) and row[y] > 0]
    if not vals: return np.nan
    return max(vals[-2:]) if len(vals) >= 2 else vals[-1]

def mov_avg(row, yr_list):
    vals = [row[y] for y in yr_list if y in row.index and pd.notna(row[y]) and row[y] > 0]
    return np.mean(vals) if vals else np.nan

def mixed_error(actual, pred):
    mask = ~(pd.isna(actual) | pd.isna(pred))
    a, p = actual[mask], pred[mask]
    if len(a) == 0: return np.nan, np.nan, np.nan
    mae = np.abs(a - p).mean()
    mae_pct = mae / a.mean() * 100
    sum_err = abs(a.sum() - p.sum()) / a.sum() * 100
    return mae_pct, sum_err, ALPHA * mae_pct + (1 - ALPHA) * sum_err

# Validação backtesting
train_v = [2021, 2022, 2023, 2024]
val_rows = []
for label, wide in [("Região", make_wide(df, ["Region"], "Qty")),
                    ("Produto", wide_prod),
                    ("Cliente×Prod", wide_cli)]:
    sub = wide.dropna(subset=[2025]).copy()
    sub["pred_max2"] = sub.apply(lambda r: max2(r, train_v), axis=1)
    sub["pred_ma"]   = sub.apply(lambda r: mov_avg(r, train_v), axis=1)
    sub = sub.dropna(subset=["pred_max2","pred_ma"])
    mp2, sp2, mix2 = mixed_error(sub[2025], sub["pred_max2"])
    mma, sma, mixm = mixed_error(sub[2025], sub["pred_ma"])
    val_rows.append({"Nível": label, "Mixed% Max2": mix2, "Mixed% MA": mixm})

df_val = pd.DataFrame(val_rows)
# Renomear Cliente×Prod para Cliente×Produto
df_val["Nível"] = df_val["Nível"].str.replace("Cliente×Prod", "Cliente×Produto")

# Previsão 2026
train_pred = [2022, 2023, 2024, 2025]
wide_cli["qty_2026"] = wide_cli.apply(lambda r: max2(r, train_pred), axis=1)

df_ph = df.copy()
df_ph["cli_enc"] = LabelEncoder().fit_transform(df_ph["Client"].astype(str))
knn_p = KNeighborsRegressor(n_neighbors=5)
knn_p.fit(df_ph[["Year","prod_enc","cli_enc","Qty"]].fillna(0), df_ph["Price"])
prod_enc_map = dict(zip(df_ph["Product"], df_ph["prod_enc"]))

wide_cli_pred = wide_cli[["Client","Product","qty_2026"]].copy()

# Por Produto
pred_by_prod = wide_cli_pred.groupby("Product")["qty_2026"].sum().reset_index()
pred_by_prod.columns = ["Product","qty_2026_bu"]
wide_prod_c = wide_prod.copy()
wide_prod_c["qty_2026_direct"] = wide_prod_c.apply(lambda r: max2(r, train_pred), axis=1)
pred_by_prod = pred_by_prod.merge(wide_prod_c[["Product","qty_2026_direct"]], on="Product", how="left")

for idx, row in pred_by_prod.iterrows():
    pe  = prod_enc_map.get(row["Product"], 0)
    qty = row["qty_2026_bu"] if not pd.isna(row["qty_2026_bu"]) else 0
    pred_by_prod.loc[idx, "price_2026"] = knn_p.predict(np.array([[YEAR_PRED, pe, 0, qty]]))[0]

price_2025    = df[df["Year"]==2025].groupby("Product")["Price"].mean()
qty_2025_prod = df[df["Year"]==2025].groupby("Product")["Qty"].sum()
# CORREÇÃO: a receita real de 2025 é a soma direta de cada transação (Qty×Price linha a
# linha), não a quantidade total multiplicada pelo preço médio — os dois só coincidem se
# o preço fosse constante em todas as transações do produto, o que não é o caso.
_rev_2025_real = df[df["Year"]==2025].assign(_r=df["Qty"]*df["Price"]).groupby("Product")["_r"].sum()
pred_by_prod["price_2025"]   = pred_by_prod["Product"].map(price_2025)
pred_by_prod["qty_2025"]     = pred_by_prod["Product"].map(qty_2025_prod)
pred_by_prod["revenue_2026"] = pred_by_prod["qty_2026_bu"] * pred_by_prod["price_2026"]
pred_by_prod["revenue_2025"] = pred_by_prod["Product"].map(_rev_2025_real)

# Por Região×Produto
# CORREÇÃO: clientes com histórico em mais do que uma região (ex. Cliente 2023, em A e C)
# não podem ser simplesmente duplicados via merge — a sua previsão 2026 é repartida
# proporcionalmente ao peso histórico (Qty) de cada região para esse cliente.
_cli_reg_qty = df.groupby(["Client","Region"])["Qty"].sum().reset_index()
_cli_reg_qty["peso_regiao"] = _cli_reg_qty["Qty"] / _cli_reg_qty.groupby("Client")["Qty"].transform("sum")

wide_cli_reg_prod = wide_cli_pred.merge(
    _cli_reg_qty[["Client","Region","peso_regiao"]], on="Client", how="left")
wide_cli_reg_prod["qty_2026_rep"] = wide_cli_reg_prod["qty_2026"] * wide_cli_reg_prod["peso_regiao"]
pred_rp = wide_cli_reg_prod.groupby(["Region","Product"])["qty_2026_rep"].sum().reset_index()
pred_rp.columns = ["Region","Product","qty_2026_bu"]

rev_2025_rp = df[df["Year"]==2025].copy()
rev_2025_rp["rev"] = rev_2025_rp["Qty"] * rev_2025_rp["Price"]
qty_2025_rp  = rev_2025_rp.groupby(["Region","Product"])["Qty"].sum().reset_index()
rev_2025_rp2 = rev_2025_rp.groupby(["Region","Product"])["rev"].sum().reset_index()
price_rp     = rev_2025_rp.groupby(["Region","Product"])["Price"].mean().reset_index()

pred_rp = pred_rp.merge(qty_2025_rp.rename(columns={"Qty":"qty_2025"}), on=["Region","Product"], how="left")
pred_rp = pred_rp.merge(rev_2025_rp2.rename(columns={"rev":"rev_2025"}), on=["Region","Product"], how="left")
pred_rp = pred_rp.merge(price_rp.rename(columns={"Price":"price_2025"}), on=["Region","Product"], how="left")
pred_rp["price_2026"] = pred_rp["price_2025"]
pred_rp["rev_2026"]   = pred_rp["qty_2026_bu"] * pred_rp["price_2026"]
pred_rp = pred_rp.fillna(0)

# Distribuir receita k-NN proporcionalmente para consistência com €6.90M
rev_knn_prod = pred_by_prod.set_index("Product")["revenue_2026"].to_dict()
_qty_tot_prod = pred_rp.groupby("Product")["qty_2026_bu"].transform("sum")
pred_rp["rev_2026"] = pred_rp.apply(
    lambda r: (r["qty_2026_bu"] / _qty_tot_prod[r.name]) * rev_knn_prod.get(r["Product"], 0)
    if _qty_tot_prod[r.name] > 0 else 0, axis=1
)

total_rev_2025 = pred_by_prod["revenue_2025"].sum()
total_rev_2026 = pred_by_prod["revenue_2026"].sum()
delta_rev = (total_rev_2026 - total_rev_2025) / total_rev_2025 * 100

print(f"  Revenue 2025: €{total_rev_2025:,.0f} → 2026: €{total_rev_2026:,.0f} ({delta_rev:+.1f}%)")

# ── HTS Validação
niveis = df_val["Nível"].tolist()
fig_val = go.Figure()
fig_val.add_trace(go.Bar(
    name="Max2", x=niveis, y=df_val["Mixed% Max2"].tolist(),
    marker_color=GREEN,
    text=[f"{v:.1f}%" for v in df_val["Mixed% Max2"]],
    textposition="outside", width=0.28,
))
fig_val.add_trace(go.Bar(
    name="Moving Average", x=niveis, y=df_val["Mixed% MA"].tolist(),
    marker_color=RED,
    text=[f"{v:.1f}%" for v in df_val["Mixed% MA"]],
    textposition="outside", width=0.28,
))
fig_val.add_trace(go.Scatter(
    x=niveis, y=[10]*len(niveis), mode="lines",
    name="Limite aceitável (10%)",
    line=dict(color="#95A5A6", dash="dash", width=1.8), hoverinfo="skip",
))
fig_val.update_layout(**bl("HTS — Backtesting 2025: Erro por Nível Hierárquico", h=420), barmode="group")
fig_val.update_xaxes(showgrid=False, title="Nível Hierárquico")
fig_val.update_yaxes(title="Erro (%)", gridcolor="#EAECEE", range=[0, 25])
interp_val = f"O modelo Max2 supera a Moving Average em todos os níveis hierárquicos — Região ({df_val.iloc[0]['Mixed% Max2']:.2f}% vs {df_val.iloc[0]['Mixed% MA']:.2f}%), Produto ({df_val.iloc[1]['Mixed% Max2']:.2f}% vs {df_val.iloc[1]['Mixed% MA']:.2f}%) e Cliente×Produto ({df_val.iloc[2]['Mixed% Max2']:.2f}% vs {df_val.iloc[2]['Mixed% MA']:.2f}%). Todos os erros do Max2 ficam abaixo do limite aceitável de 10%, justificando a sua seleção como modelo de previsão de quantidade."

# ── P1 Quantidade por Produto
anos_lbl = [str(y) for y in YEARS_ALL] + ["2026 ▶"]
fig_p1 = go.Figure()
for prod in PRODUTOS:
    hist = [wide_prod[wide_prod["Product"]==prod][y].values[0]
            if not wide_prod[wide_prod["Product"]==prod].empty else 0 for y in YEARS_ALL]
    qty26 = pred_by_prod[pred_by_prod["Product"]==prod]["qty_2026_bu"].values[0]
    y_all = [v if not pd.isna(v) else 0 for v in hist] + [qty26]
    fig_p1.add_trace(go.Bar(
        name=f"Produto {prod}", x=anos_lbl, y=y_all,
        marker_color=PROD_C[prod],
        hovertemplate=f"<b>Produto {prod}</b> — %{{x}}<br>Qty: %{{y:,.0f}}<extra></extra>",
    ))
fig_p1.update_layout(**bl("P1 — Quantidade por Produto: Histórico 2021–2025 e Previsão 2026", h=420), barmode="stack")
fig_p1.update_xaxes(showgrid=False, title="Ano")
fig_p1.update_yaxes(title="Quantidade", gridcolor="#EAECEE", tickformat=".2s")
fig_p1.add_vrect(x0=4.5, x1=5.5, fillcolor="rgba(46,134,193,0.07)", line_width=0,
    annotation_text="Previsão", annotation_position="top right",
    annotation_font=dict(size=10, color="#2E86C1"))
fig_p1.add_vline(x=4.5, line_dash="dash", line_color=AMBER, line_width=1.5)
interp_p1 = "A quantidade total prevista para 2026 é de aproximadamente 3.84M unidades, representando um forte crescimento face a 2025. O Produto B reforça-se como principal contribuinte em volume, seguido pelo Produto A, enquanto os Produtos C e D permanecem com menor peso relativo."

# ── P2 Receita por Produto
_deltas = [(pred_by_prod[pred_by_prod["Product"]==p]["revenue_2026"].values[0] -
            pred_by_prod[pred_by_prod["Product"]==p]["revenue_2025"].values[0]) /
           pred_by_prod[pred_by_prod["Product"]==p]["revenue_2025"].values[0] * 100
           for p in PRODUTOS]
fig_p2 = go.Figure()
fig_p2.add_trace(go.Bar(
    name="2025 Real",
    x=[f"Produto {p}" for p in PRODUTOS],
    y=[pred_by_prod[pred_by_prod["Product"]==p]["revenue_2025"].values[0] for p in PRODUTOS],
    marker_color=[PROD_C[p] for p in PRODUTOS], opacity=0.55,
    text=[f"€{pred_by_prod[pred_by_prod['Product']==p]['revenue_2025'].values[0]/1e6:.2f}M"
          if pred_by_prod[pred_by_prod['Product']==p]['revenue_2025'].values[0] >= 500000
          else f"€{pred_by_prod[pred_by_prod['Product']==p]['revenue_2025'].values[0]/1e3:.0f}k"
          for p in PRODUTOS],
    textposition="outside"))
fig_p2.add_trace(go.Bar(
    name="2026 Prev.",
    x=[f"Produto {p}" for p in PRODUTOS],
    y=[pred_by_prod[pred_by_prod["Product"]==p]["revenue_2026"].values[0] for p in PRODUTOS],
    marker_color=[PROD_C[p] for p in PRODUTOS],
    text=[f"€{pred_by_prod[pred_by_prod['Product']==p]['revenue_2026'].values[0]/1e6:.2f}M"
          if pred_by_prod[pred_by_prod['Product']==p]['revenue_2026'].values[0] >= 500000
          else f"€{pred_by_prod[pred_by_prod['Product']==p]['revenue_2026'].values[0]/1e3:.0f}k"
          for p in PRODUTOS],
    textposition="outside"))
for i, prod in enumerate(PRODUTOS):
    rev26 = pred_by_prod[pred_by_prod["Product"]==prod]["revenue_2026"].values[0]
    fig_p2.add_annotation(x=f"Produto {prod}", y=rev26, text=f"<b>{_deltas[i]:+.1f}%</b>",
        showarrow=False, yshift=22, font=dict(size=11, color=NAVY, family=FONT))
fig_p2.update_layout(**bl("P2 — Receita 2025 vs Receita Prevista 2026 por Produto"), barmode="group")
fig_p2.update_xaxes(showgrid=False)
fig_p2.update_yaxes(title="Receita (€M)", gridcolor="#EAECEE",
    tickformat=".2f", ticksuffix="M",
    tickvals=[0, 500000, 1000000, 1500000, 2000000, 2500000, 3000000, 3500000],
    ticktext=["€0M","€0.5M","€1.0M","€1.5M","€2.0M","€2.5M","€3.0M","€3.5M"])
interp_p2 = "O Produto B ultrapassa o Produto A como principal fonte de receita prevista em 2026 (€3.56M vs €2.84M), com crescimento de +77.5%. O Produto A cresce +8.5%, sugerindo maturação face ao forte crescimento do Produto B. Os Produtos C e D registam crescimentos percentuais elevados, mas partem de bases de receita reduzidas."

# ── W1 Waterfall
_rev25 = [pred_by_prod[pred_by_prod["Product"]==p]["revenue_2025"].values[0] for p in PRODUTOS]
_rev26 = [pred_by_prod[pred_by_prod["Product"]==p]["revenue_2026"].values[0] for p in PRODUTOS]
_deltas_wf = [r26 - r25 for r25, r26 in zip(_rev25, _rev26)]
_total_delta = sum(_deltas_wf)
_top_idx = _deltas_wf.index(max(_deltas_wf))
_top_prod = PRODUTOS[_top_idx]
_top_pct  = _deltas_wf[_top_idx] / _total_delta * 100

_wf_text = [f"€{sum(_rev25)/1e6:.2f}M"] + \
           [f"+€{d/1e6:.2f}M" if d >= 500000 else f"+€{round(d/1e3):.0f}k" for d in _deltas_wf] + \
           [f"€{sum(_rev26)/1e6:.2f}M"]

fig_wf = go.Figure(go.Waterfall(
    orientation="v",
    measure=["absolute"] + ["relative"]*len(PRODUTOS) + ["total"],
    x=["2025 Base"] + [f"Produto {p}" for p in PRODUTOS] + ["2026 Total"],
    y=[sum(_rev25)] + _deltas_wf + [sum(_rev26)],
    text=_wf_text, textposition="outside",
    connector=dict(line=dict(color="#D5D8DC", width=1)),
    increasing=dict(marker=dict(color=GREEN)),
    decreasing=dict(marker=dict(color=RED)),
    totals=dict(marker=dict(color=AMBER)),
))
fig_wf.add_annotation(
    xref="paper", yref="paper", x=0.01, y=0.97,
    text=f"<b>TOP GROWTH DRIVER</b> · Produto {_top_prod} · <b>+€{_deltas_wf[_top_idx]/1e6:.2f}M</b> ({_top_pct:.1f}% do crescimento)",
    showarrow=False, align="left",
    font=dict(size=11, color=GREEN, family=FONT),
    bgcolor="rgba(255,255,255,0.92)", bordercolor=GREEN, borderwidth=1, borderpad=8,
    xanchor="left", yanchor="top")
fig_wf.update_layout(**bl("W1 — Variação da Receita 2025 → 2026 por Produto (Waterfall)", h=440))
fig_wf.update_xaxes(showgrid=False)
fig_wf.update_yaxes(title="Receita (€)", gridcolor="#EAECEE",
    tickvals=[4500000,5000000,5500000,6000000,6500000,7000000],
    ticktext=["€4.5M","€5.0M","€5.5M","€6.0M","€6.5M","€7.0M"],
    range=[4_500_000, 7_400_000])
interp_wf = f"O Produto B é responsável por {_top_pct:.1f}% do crescimento total previsto (+€{_deltas_wf[_top_idx]/1e6:.2f}M). O crescimento encontra-se fortemente concentrado neste produto, sugerindo risco de dependência estratégica num único driver de receita."

# ── RP1 Heatmap Região×Produto
regioes_rp = sorted(pred_rp["Region"].unique(), reverse=True)  # E→A, heatmap inverte → RA no topo
matrix_26 = []
for reg in regioes_rp:
    row = []
    for prod in PRODUTOS:
        sub = pred_rp[(pred_rp["Region"]==reg) & (pred_rp["Product"]==prod)]
        row.append(round(sub["rev_2026"].values[0]/1e3, 1) if len(sub)>0 else 0)
    matrix_26.append(row)

def _fmt_cell(v):
    if v <= 0: return "—"
    if v >= 1000: return f"€{v/1000:.2f}M"
    return f"€{v:.0f}k"

fig_rp1 = go.Figure(go.Heatmap(
    z=matrix_26,
    x=[f"Produto {p}" for p in PRODUTOS],
    y=[f"Região {r}" for r in regioes_rp],
    colorscale="YlGnBu",
    text=[[_fmt_cell(v) for v in row] for row in matrix_26],
    texttemplate="%{text}",
    textfont=dict(size=11, family=FONT),
    hovertemplate="<b>%{y} × %{x}</b><br>Receita 2026: %{text}<extra></extra>",
    showscale=True,
    colorbar=dict(title="Receita prevista (€k)"),
))
fig_rp1.update_layout(**bl("RP1 — Heatmap Receita 2026: Região × Produto", h=400))
fig_rp1.update_xaxes(showgrid=False)
fig_rp1.update_yaxes(showgrid=False)
interp_rp1 = "A combinação Região A × Produto A concentra a maior receita prevista em 2026, seguida por Região A × Produto B. A Região B apresenta peso relevante sobretudo no Produto A, enquanto os Produtos C e D mantêm impacto residual na maioria das regiões."

# ── RP2 Variação % Região×Produto
fig_rp2 = go.Figure()
for prod in PRODUTOS:
    sub = pred_rp[pred_rp["Product"]==prod].copy()
    sub = sub[sub["rev_2025"]>0].copy()
    sub["delta_pct"] = (sub["rev_2026"]-sub["rev_2025"])/sub["rev_2025"]*100
    fig_rp2.add_trace(go.Bar(
        name=f"Produto {prod}",
        x=[f"Região {r}" for r in sub["Region"]],
        y=sub["delta_pct"].round(1).tolist(),
        marker_color=PROD_C[prod],
        text=[f"{v:+.1f}%" for v in sub["delta_pct"].round(1)],
        textposition="outside",
        hovertemplate=f"<b>Produto {prod}</b> — %{{x}}<br>Δ: %{{y:+.1f}}%<extra></extra>",
    ))
fig_rp2.update_layout(**bl("RP2 — Variação de Receita 2025→2026 por Região × Produto (%)", h=420), barmode="group")
fig_rp2.update_xaxes(showgrid=False)
fig_rp2.update_yaxes(title="Variação (%)", gridcolor="#EAECEE", zeroline=True, zerolinecolor="#D5D8DC")
fig_rp2.add_hline(y=0, line_color="#95A5A6", line_width=1)
interp_rp2 = "A Região B concentra os maiores crescimentos percentuais, com destaque para Produto D (+530.3%). As Regiões C, D e E apresentam apenas um produto activo em 2025 (com receita registada), pelo que só esse produto aparece no gráfico — ausência de barra não significa crescimento zero, mas ausência de actividade comparável nessa combinação. Estes valores devem ser interpretados com cautela: crescimentos elevados em Produtos C e D partem de bases de receita reduzidas. O RP2 complementa o RP1: mostra intensidade relativa de crescimento, mas não substitui a análise do impacto absoluto em receita."

# ── Tabela RP
tbl_rp = pred_rp[pred_rp["rev_2025"]>0].copy()

# Distribuir receita k-NN proporcionalmente pela quantidade de cada Região×Produto
# para garantir que o total bate com os €6.90M dos KPIs
rev_knn_prod = pred_by_prod.set_index("Product")["revenue_2026"].to_dict()
qty_total_prod = tbl_rp.groupby("Product")["qty_2026_bu"].transform("sum")
tbl_rp["rev_2026_knn"] = tbl_rp.apply(
    lambda r: (r["qty_2026_bu"] / qty_total_prod[r.name]) * rev_knn_prod.get(r["Product"], 0)
    if qty_total_prod[r.name] > 0 else 0, axis=1
)

tbl_rp["Δ Rev%"] = ((tbl_rp["rev_2026_knn"]-tbl_rp["rev_2025"])/tbl_rp["rev_2025"]*100).round(1)
tbl_rp = tbl_rp.sort_values(["Region","Product"])

# Linha de totais
_tot_qty25 = tbl_rp["qty_2025"].sum()
_tot_qty26 = tbl_rp["qty_2026_bu"].sum()
_tot_rev25 = tbl_rp["rev_2025"].sum()
_tot_rev26 = tbl_rp["rev_2026_knn"].sum()
_tot_delta = (_tot_rev26 - _tot_rev25) / _tot_rev25 * 100

_regions = tbl_rp["Region"].tolist() + ["TOTAL"]
_products = tbl_rp["Product"].tolist() + ["—"]
_qty25    = [f"{v:,.0f}" for v in tbl_rp["qty_2025"]] + [f"{_tot_qty25:,.0f}"]
_qty26    = [f"{v:,.0f}" for v in tbl_rp["qty_2026_bu"]] + [f"{_tot_qty26:,.0f}"]
_rev25    = [f"€{v:,.0f}" for v in tbl_rp["rev_2025"]] + [f"€{_tot_rev25:,.0f}"]
_rev26    = [f"€{v:,.0f}" for v in tbl_rp["rev_2026_knn"]] + [f"€{_tot_rev26:,.0f}"]
_delta    = [f"{v:+.1f}%" for v in tbl_rp["Δ Rev%"]] + [f"{_tot_delta:+.1f}%"]

_n = len(_regions)
_fill = [["#F2F3F4" if i%2==0 else "white" for i in range(_n-1)] + [AMBER] for _ in range(7)]

fig_tbl_rp = go.Figure(go.Table(
    header=dict(
        values=["Região","Produto","Qty 2025","Qty 2026 Bottom-Up","Rev 2025","Rev 2026","Variação Receita %"],
        fill_color=NAVY, font=dict(color="white",size=11,family=FONT),
        align="center", height=30),
    cells=dict(
        values=[_regions, _products, _qty25, _qty26, _rev25, _rev26, _delta],
        fill_color=_fill,
        font=dict(size=10, family=FONT), align="center", height=26)
))
fig_tbl_rp.update_layout(**bl("Tabela — Combinações Ativas Região × Produto: Previsão 2026", h=560))
interp_tbl = "Tabela analítica com todas as combinações Região×Produto com atividade registada. A linha Total confirma a receita prevista global para 2026 e a variação face a 2025. Permite auditoria quantitativa e suporte direto à defesa oral."

# MONTAR HTML

print("A gerar HTML...")

def section(title, ref, figs_html, interp, cols=2):
    cards = "".join(f'<div class="card">{f}</div>' for f in figs_html)
    grid = f'<div class="g{cols}">{cards}</div>' if cols > 1 else f'<div class="g1">{cards}</div>'
    return f'''
<div class="sec">{title}</div>
<div class="ref">{ref}</div>
{grid}
<div class="box"><strong>Interpretação:</strong> {interp}</div>
'''

html = f"""<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard Pré-Final — DW & BI Vendas</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'EB Garamond',Georgia,serif;background:#F7F9FB;color:#1C2833}}
.hdr{{background:linear-gradient(135deg,#1a3a5c 0%,#2d6a9f 100%);color:white;padding:2rem 2.5rem}}
.hdr h1{{font-size:1.9rem;font-weight:600}}
.hdr p{{font-size:0.85rem;opacity:0.65;margin-top:0.3rem;font-family:'DM Mono',monospace}}
.kpis{{display:grid;grid-template-columns:repeat(5,1fr);gap:0.8rem;padding:1.2rem 1.5rem}}
.kpi{{background:white;border-radius:6px;padding:0.9rem 1rem;
      border-top:3px solid #1B4F72;box-shadow:0 2px 6px rgba(0,0,0,0.07);text-align:center}}
.kpi .v{{font-size:1.4rem;font-weight:700;color:#0D1B2A}}
.kpi .l{{font-size:0.72rem;color:#7F8C8D;font-family:'DM Mono',monospace;margin-top:0.2rem}}
.phase-hdr{{padding:0.6rem 1.5rem;margin:0.5rem 0 0;
            font-size:1.05rem;font-weight:700;color:white;
            display:flex;align-items:center;gap:0.6rem}}
.phase-hdr.olap{{background:#0D1B2A}}
.phase-hdr.hts{{background:#1E8449}}
.sec{{font-size:0.92rem;font-weight:600;color:#0D1B2A;
      margin:0.5rem 1.5rem 0.2rem;padding-left:0.8rem;
      border-left:3px solid #2E86C1}}
.ref{{font-size:0.74rem;color:#7F8C8D;font-style:italic;
      padding:0 1.5rem 0.6rem;font-family:'DM Mono',monospace}}
.g2{{display:grid;grid-template-columns:1fr 1fr;gap:0.8rem;padding:0 1.5rem;margin-bottom:0.6rem}}
.g1{{padding:0 1.5rem;margin-bottom:0.6rem}}
.card{{background:white;border-radius:6px;padding:0.3rem;
       box-shadow:0 2px 6px rgba(0,0,0,0.07)}}
.box{{background:#EBF5FB;border-left:4px solid #2E86C1;
      padding:0.75rem 1.1rem;margin:0 1.5rem 1rem;border-radius:4px;
      font-size:0.86rem;line-height:1.6}}
.box strong{{color:#1B4F72}}
.ft{{text-align:center;padding:1.2rem;font-size:0.76rem;color:#7F8C8D;
     border-top:1px solid #D5D8DC;margin-top:1rem;font-family:'DM Mono',monospace}}
</style>
</head>
<body>

<div class="hdr">
  <h1>Dashboard Pré-Final — Data Warehouse &amp; BI de Vendas</h1>
  <p>14 Visualizações + 1 Tabela Analítica · OLAP Histórico · Forecasting HTS · Região × Produto · 2021–2026</p>
</div>

<div class="kpis">
  <div class="kpi" style="border-top-color:#E8837A">
    <div class="v">€{df['Valor_Total'].sum()/1e6:.1f}M</div><div class="l">Receita Total 2021–2025</div>
  </div>
  <div class="kpi" style="border-top-color:#4CAF50">
    <div class="v">{df['Client'].nunique()}</div><div class="l">Clientes Únicos</div>
  </div>
  <div class="kpi">
    <div class="v">4 × 5</div><div class="l">Produtos × Regiões</div>
  </div>
  <div class="kpi" style="border-top-color:#D68910">
    <div class="v">€{total_rev_2026/1e6:.2f}M</div><div class="l">Receita Prevista 2026</div>
  </div>
  <div class="kpi" style="border-top-color:#1E8449">
    <div class="v">{delta_rev:+.1f}%</div><div class="l">Crescimento Previsto</div>
  </div>
</div>

<div class="phase-hdr olap">📊 Fase 2 — Análise OLAP Histórica (7 visualizações)</div>

{section("Q01 — Roll-Up: Evolução Global de Vendas",
    "Agregação anual · operação Roll-Up sobre a dimensão Tempo",
    [to_div(fig_q01)], interp_q01, cols=1)}

{section("Q02 — Drill-Down: Vendas por Ano e Região",
    "Desagregação regional · cuboide T×R · barras empilhadas por ano",
    [to_div(fig_q02)], interp_q02, cols=1)}

{section("Q04 — Market Share: Quota % por Região e Ano",
    "Evolução da quota de mercado por região · cuboide T×R",
    [to_div(fig_q04)], interp_q04, cols=1)}

{section("Q05 — Crescimento Anual de Vendas (YoY)",
    "Taxa de crescimento anual · variação percentual face ao ano anterior",
    [to_div(fig_q05)], interp_q05, cols=1)}

{section("Q06 — Pareto 80/20: Segmentação de Clientes (Top 30)",
    "Análise Pareto 80/20 dos clientes · concentração de receita",
    [to_div(fig_q06)], interp_q06, cols=1)}

{section("Q07 — Pivot: Valor Total por Produto × Ano",
    "Análise multidimensional por produto · barras agrupadas por ano",
    [to_div(fig_q07)], interp_q07, cols=1)}

{section("Q08 — Cuboide OLAP: Ano × Região × Produto",
    "Cuboide Tempo × Região × Produto · matrizes Região×Produto por ano",
    [to_div(fig_q08)], interp_q08, cols=1)}

<div class="phase-hdr hts">🔮 Fase 3 — Forecasting HTS (7 visualizações + 1 tabela)</div>

{section("Validação Backtesting — Max2 vs Moving Average",
    "Treino 2021–2024 · previsão 2025 · validação por backtesting",
    [to_div(fig_val)], interp_val, cols=1)}

{section("P1 — Quantidade por Produto: Histórico 2021–2025 e Previsão 2026",
    "Max2 Bottom-Up · quantidade prevista por produto · separação histórico/previsão",
    [to_div(fig_p1)], interp_p1, cols=1)}

{section("P2 — Receita 2025 vs Receita Prevista 2026 por Produto",
    "KNN exploratório (preço) · Receita = Qty × Preço · variação percentual 2025→2026",
    [to_div(fig_p2)], interp_p2, cols=1)}

{section("W1 — Decomposição do Crescimento da Receita (Waterfall)",
    "Contribuição de cada produto para o crescimento de receita 2025→2026",
    [to_div(fig_wf)], interp_wf, cols=1)}

{section("RP1 — Heatmap Receita 2026: Região × Produto",
    "Receita prevista por combinação Região × Produto · escala de intensidade por receita prevista",
    [to_div(fig_rp1)], interp_rp1, cols=1)}

{section("RP2 — Variação de Receita 2025→2026 por Região × Produto (%)",
    "Crescimento percentual por combinação Região × Produto · crescimentos elevados podem refletir bases de receita reduzidas",
    [to_div(fig_rp2)], interp_rp2, cols=1)}

{section("Tabela Analítica — Combinações Ativas Região × Produto",
    "Tabela de suporte · dados numéricos completos · linha de totais para auditoria e defesa oral",
    [to_div(fig_tbl_rp)], interp_tbl, cols=1)}

<div class="ft">
  Gonçalo Meixieiro · Ulisses Nascimento &nbsp;|&nbsp;
  Projeto Final — Data Warehouse &amp; BI &nbsp;|&nbsp;
  Universidade Aberta · Prof. Luís Cavique · 2026
</div>
</body>
</html>"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"\n[OK] {OUT}")
print(f"  15 visualizações · paleta do professor · interpretações incluídas")