from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PROCESSED = DATA / "processed"
PORTFOLIO = DATA / "portfolio"

COLORS = {
    "Hidrelétrica": "#1b9aaa",
    "PCH/CGH": "#48a868",
    "Eólica": "#6f7bd9",
    "Solar": "#f2b134",
    "Biomassa": "#7aa95c",
    "Gás Natural": "#9c6ade",
    "Óleo": "#c65d57",
    "Carvão": "#555555",
    "Nuclear": "#e06c9f",
    "Térmica Outras": "#a06b45",
    "Outras": "#7d8790",
}


st.set_page_config(
    page_title="Sistema Elétrico Brasileiro",
    page_icon="⚡",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def br_number(value: float, decimals: int = 1) -> str:
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def metric_value(kpis: pd.DataFrame, name: str) -> tuple[float, str, str]:
    row = kpis.loc[kpis["Indicador"].eq(name)].head(1)
    if row.empty:
        return 0.0, "", ""
    return float(row.iloc[0]["Valor"]), str(row.iloc[0]["Unidade"]), str(row.iloc[0]["Escopo"])


def bar(df: pd.DataFrame, x: str, y: str, title: str, color: str | None = None, orientation: str = "v") -> go.Figure:
    fig = px.bar(df, x=x, y=y, color=color, title=title, orientation=orientation, color_discrete_map=COLORS)
    fig.update_layout(template="plotly_white", title_x=0.02, legend_title_text="", margin=dict(l=10, r=10, t=60, b=10))
    return fig


def line(df: pd.DataFrame, x: str, y: str, title: str, color: str | None = None) -> go.Figure:
    fig = px.line(df, x=x, y=y, color=color, title=title, color_discrete_map=COLORS)
    fig.update_layout(template="plotly_white", title_x=0.02, legend_title_text="", margin=dict(l=10, r=10, t=60, b=10))
    return fig


kpis = load_csv(PROCESSED / "kpi_snapshot.csv")
cap_source = load_csv(PORTFOLIO / "capacidade_por_fonte.csv")
cap_uf = load_csv(PORTFOLIO / "capacidade_por_uf.csv")
gen_source = load_csv(PORTFOLIO / "geracao_por_fonte.csv")
gen_month = load_csv(PORTFOLIO / "geracao_mensal.csv")
load_sin = load_csv(PORTFOLIO / "carga_sin.csv")
mmgd_uf = load_csv(PORTFOLIO / "mmgd_por_uf.csv")
pld = load_csv(PORTFOLIO / "pld.csv")
capacity_detail = load_csv(PROCESSED / "Fato_CapacidadeInstalada.csv")
mmgd_detail = load_csv(PROCESSED / "Fato_MMGD.csv")

st.title("Dashboard Analítico do Sistema Elétrico Brasileiro")
st.caption("Bases oficiais ANEEL, ONS e CCEE | modelo dimensional local | guardrails de unidade aplicados")

with st.sidebar:
    st.header("Filtros")
    available_regions = sorted(set(cap_uf.get("Regiao", pd.Series(dtype=str)).dropna()) | set(mmgd_uf.get("Regiao", pd.Series(dtype=str)).dropna()))
    regions = st.multiselect("Região", available_regions, default=available_regions)
    available_ufs = sorted(set(cap_uf.loc[cap_uf["Regiao"].isin(regions), "UF"].dropna()) if regions and not cap_uf.empty else set(cap_uf.get("UF", [])))
    ufs = st.multiselect("UF", available_ufs, default=available_ufs)
    source_options = sorted(set(cap_source.get("FonteExibicao", pd.Series(dtype=str)).dropna()) | set(gen_source.get("FonteExibicao", pd.Series(dtype=str)).dropna()))
    sources = st.multiselect("Fonte", source_options, default=source_options)

cap_source_f = cap_source[cap_source["FonteExibicao"].isin(sources)] if not cap_source.empty and sources else cap_source
cap_uf_f = cap_uf[cap_uf["UF"].isin(ufs)] if not cap_uf.empty and ufs else cap_uf
gen_source_f = gen_source[gen_source["FonteExibicao"].isin(sources)] if not gen_source.empty and sources else gen_source
gen_month_f = gen_month[gen_month["FonteExibicao"].isin(sources)] if not gen_month.empty and sources else gen_month
mmgd_uf_f = mmgd_uf[(mmgd_uf["UF"].isin(ufs)) & (mmgd_uf["FonteExibicao"].isin(sources))] if not mmgd_uf.empty and ufs and sources else mmgd_uf
capacity_detail_f = capacity_detail[(capacity_detail["UF"].isin(ufs)) & (capacity_detail["FonteExibicao"].isin(sources))] if not capacity_detail.empty and ufs and sources else capacity_detail

tabs = st.tabs([
    "Visão Executiva",
    "Matriz de Geração",
    "Geração do SIN",
    "Carga do SIN",
    "Energias Renováveis",
    "Geração Distribuída",
    "Análise Geográfica",
    "Expansão",
    "Mercado de Energia",
    "Detalhamento por Estado",
    "Detalhamento por Fonte",
])

with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    cap, unit, scope = metric_value(kpis, "Capacidade instalada operacional")
    ren, _, _ = metric_value(kpis, "Participação renovável na capacidade")
    energy, eunit, _ = metric_value(kpis, "Energia gerada no período ONS")
    load_avg, lunit, _ = metric_value(kpis, "Carga média SIN")
    c1.metric("Capacidade operacional", f"{br_number(cap, 0)} {unit}")
    c2.metric("Renovável na capacidade", f"{br_number(ren, 1)}%")
    c3.metric("Energia ONS", f"{br_number(energy, 1)} {eunit}")
    c4.metric("Carga média SIN", f"{br_number(load_avg, 0)} {lunit}")
    st.plotly_chart(bar(cap_source_f.sort_values("Potencia_MW", ascending=False), "FonteExibicao", "Potencia_MW", "Capacidade operacional por fonte", "FonteExibicao"), use_container_width=True)
    st.dataframe(kpis, use_container_width=True, hide_index=True)

with tabs[1]:
    cap_cmp = cap_source.rename(columns={"Potencia_MW": "Valor"})
    cap_cmp["Métrica"] = "Capacidade instalada (MW)"
    gen_cmp = gen_source.rename(columns={"Energia_MWh": "Valor"})
    gen_cmp["Valor"] = gen_cmp["Valor"] / 1_000_000
    gen_cmp["Métrica"] = "Energia gerada (TWh)"
    cmp = pd.concat([cap_cmp[["FonteExibicao", "Valor", "Métrica"]], gen_cmp[["FonteExibicao", "Valor", "Métrica"]]], ignore_index=True)
    st.plotly_chart(bar(cmp, "FonteExibicao", "Valor", "Capacidade e energia por fonte, em unidades separadas", "Métrica"), use_container_width=True)
    st.caption("Capacidade está em MW; energia está em TWh. O painel não soma MWmed para representar volume.")

with tabs[2]:
    if not gen_month_f.empty:
        monthly = gen_month_f.copy()
        monthly["Mes"] = pd.to_datetime(monthly["Data"]).dt.to_period("M").astype(str)
        monthly = monthly.groupby(["Mes", "FonteExibicao"], as_index=False)["Energia_MWh"].sum()
        monthly["Energia_TWh"] = monthly["Energia_MWh"] / 1_000_000
        st.plotly_chart(line(monthly, "Mes", "Energia_TWh", "Energia mensal por fonte no SIN", "FonteExibicao"), use_container_width=True)
        st.dataframe(monthly.sort_values(["Mes", "FonteExibicao"], ascending=[False, True]).head(200), use_container_width=True, hide_index=True)

with tabs[3]:
    if not load_sin.empty:
        load = load_sin.copy()
        load["DataHora"] = pd.to_datetime(load["DataHora"])
        daily = load.groupby(load["DataHora"].dt.date, as_index=False)["CargaSIN_MWmed"].mean()
        daily.columns = ["Data", "CargaSIN_MWmed"]
        st.plotly_chart(line(daily, "Data", "CargaSIN_MWmed", "Carga média diária do SIN"), use_container_width=True)
        peak = load.loc[load["CargaSIN_MWmed"].idxmax()]
        st.metric("Pico do recorte", f"{br_number(float(peak['CargaSIN_MWmed']), 0)} MWmed", str(peak["DataHora"]))

with tabs[4]:
    ren = cap_source.groupby("Renovavel", as_index=False)["Potencia_MW"].sum()
    st.plotly_chart(px.pie(ren, names="Renovavel", values="Potencia_MW", title="Participação renovável na capacidade operacional"), use_container_width=True)
    renewable_sources = cap_source[cap_source["Renovavel"].eq("Sim")].sort_values("Potencia_MW", ascending=False)
    st.plotly_chart(bar(renewable_sources, "FonteExibicao", "Potencia_MW", "Fontes renováveis por capacidade", "FonteExibicao"), use_container_width=True)

with tabs[5]:
    if not mmgd_uf_f.empty:
        st.metric("Capacidade MMGD filtrada", f"{br_number(float(mmgd_uf_f['Potencia_MW'].sum()), 0)} MW")
        st.plotly_chart(bar(mmgd_uf_f.groupby("UF", as_index=False)["Potencia_MW"].sum().sort_values("Potencia_MW", ascending=False).head(15), "UF", "Potencia_MW", "Top UFs por MMGD"), use_container_width=True)
        st.plotly_chart(bar(mmgd_uf_f.groupby("FonteExibicao", as_index=False)["Potencia_MW"].sum(), "FonteExibicao", "Potencia_MW", "MMGD por fonte", "FonteExibicao"), use_container_width=True)

with tabs[6]:
    st.plotly_chart(bar(cap_uf_f.sort_values("Potencia_MW", ascending=False), "UF", "Potencia_MW", "Capacidade operacional por UF"), use_container_width=True)
    map_df = capacity_detail_f.dropna(subset=["Latitude", "Longitude"]).copy()
    map_df["Latitude"] = pd.to_numeric(map_df["Latitude"].astype(str).str.replace(",", "."), errors="coerce")
    map_df["Longitude"] = pd.to_numeric(map_df["Longitude"].astype(str).str.replace(",", "."), errors="coerce")
    map_df["Potencia_MW"] = pd.to_numeric(map_df["Potencia_MW"], errors="coerce")
    map_df = map_df.dropna(subset=["Latitude", "Longitude", "Potencia_MW"])
    if len(map_df) > 5000:
        map_df = map_df.nlargest(5000, "Potencia_MW")
        st.caption("Mapa com amostragem visual dos 5.000 maiores empreendimentos filtrados; KPIs e tabelas usam a base agregada completa.")
    if not map_df.empty:
        fig = px.scatter_mapbox(map_df, lat="Latitude", lon="Longitude", color="FonteExibicao", size="Potencia_MW", hover_name="Empreendimento", hover_data=["UF", "Potencia_MW"], zoom=3.2, height=620, color_discrete_map=COLORS)
        fig.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

with tabs[7]:
    if not capacity_detail.empty:
        expansion = capacity_detail.dropna(subset=["DataOperacao"]).copy()
        expansion["AnoOperacao"] = pd.to_datetime(expansion["DataOperacao"], errors="coerce").dt.year
        expansion = expansion.dropna(subset=["AnoOperacao"])
        by_year = expansion.groupby(["AnoOperacao", "FonteExibicao"], as_index=False)["Potencia_MW"].sum()
        st.plotly_chart(line(by_year, "AnoOperacao", "Potencia_MW", "Entrada em operação por ano e fonte", "FonteExibicao"), use_container_width=True)

with tabs[8]:
    if not pld.empty:
        pld_view = pld.copy()
        pld_view["PLD_Medio_R$/MWh"] = pd.to_numeric(pld_view["PLD_Medio_R$/MWh"], errors="coerce")
        st.plotly_chart(line(pld_view, "AnoMes", "PLD_Medio_R$/MWh", "PLD médio mensal por submercado", "Submercado"), use_container_width=True)
        st.dataframe(pld_view.sort_values(["AnoMes", "Submercado"], ascending=[False, True]), use_container_width=True, hide_index=True)
    else:
        st.info("PLD não disponível no cache local. Execute `python -m scripts.extract_ccee` e `python -m scripts.build_model`.")

with tabs[9]:
    state = cap_uf_f.groupby(["Regiao", "UF"], as_index=False)["Potencia_MW"].sum().sort_values("Potencia_MW", ascending=False)
    st.dataframe(state, use_container_width=True, hide_index=True)
    st.plotly_chart(bar(state.head(20), "Potencia_MW", "UF", "Ranking estadual de capacidade operacional", "Regiao", "h"), use_container_width=True)

with tabs[10]:
    source_table = cap_source.merge(gen_source, on="FonteExibicao", how="outer").fillna(0)
    source_table["Energia_TWh"] = source_table["Energia_MWh"] / 1_000_000
    source_table["Capacidade_%"] = source_table["Potencia_MW"] / source_table["Potencia_MW"].sum() * 100
    source_table["Energia_%"] = source_table["Energia_MWh"] / source_table["Energia_MWh"].sum() * 100
    st.dataframe(source_table[["FonteExibicao", "Renovavel", "Potencia_MW", "Capacidade_%", "Energia_TWh", "Energia_%"]].sort_values("Potencia_MW", ascending=False), use_container_width=True, hide_index=True)
    st.plotly_chart(bar(source_table.sort_values("Potencia_MW", ascending=False), "FonteExibicao", "Capacidade_%", "Participação na capacidade operacional", "FonteExibicao"), use_container_width=True)
