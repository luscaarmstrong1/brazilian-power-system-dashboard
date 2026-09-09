from __future__ import annotations

from collections import defaultdict

from src.common import ROOT, read_csv_rows, to_float


def top(items: dict[str, float], n: int = 5) -> list[tuple[str, float]]:
    return sorted(items.items(), key=lambda kv: kv[1], reverse=True)[:n]


def pct(value: float, total: float) -> float:
    return (value / total * 100) if total else 0


def main() -> None:
    capacity, _ = read_csv_rows(ROOT / "data/processed/Fato_CapacidadeInstalada.csv")
    generation_all, _ = read_csv_rows(ROOT / "data/processed/Fato_Geracao.csv")
    generation = [row for row in generation_all if str(row.get("Subsistema", "")).upper() == "SIN"] or generation_all
    load_sin, _ = read_csv_rows(ROOT / "data/processed/Fato_CargaSIN.csv")
    mmgd, _ = read_csv_rows(ROOT / "data/processed/Fato_MMGD.csv")
    pld, _ = read_csv_rows(ROOT / "data/processed/Fato_PLD.csv")

    by_source = defaultdict(float)
    by_uf = defaultdict(float)
    renewable = 0.0
    total_capacity = 0.0
    for row in capacity:
        value = to_float(row.get("Potencia_MW")) or 0
        total_capacity += value
        by_source[row.get("FonteExibicao") or "Não informado"] += value
        by_uf[row.get("UF") or "Não informado"] += value
        if row.get("Renovavel") == "Sim":
            renewable += value

    energy_by_source = defaultdict(float)
    total_energy_mwh = 0.0
    for row in generation:
        value = to_float(row.get("Energia_MWh")) or 0
        total_energy_mwh += value
        energy_by_source[row.get("FonteExibicao") or "Não informado"] += value

    mmgd_uf = defaultdict(float)
    mmgd_source = defaultdict(float)
    systems = 0
    for row in mmgd:
        value = to_float(row.get("Potencia_MW")) or 0
        mmgd_uf[row.get("UF") or "Não informado"] += value
        mmgd_source[row.get("FonteExibicao") or "Não informado"] += value
        systems += int(to_float(row.get("QuantidadeSistemas")) or 0)
    total_mmgd = sum(mmgd_uf.values())

    avg_load = sum(to_float(r.get("CargaSIN_MWmed")) or 0 for r in load_sin) / len(load_sin) if load_sin else 0
    peak = max(load_sin, key=lambda r: to_float(r.get("CargaSIN_MWmed")) or 0, default={})
    peak_value = to_float(peak.get("CargaSIN_MWmed")) or 0

    lines = [
        "# Insights do Sistema Elétrico Brasileiro",
        "",
        "Todos os achados abaixo usam bases oficiais processadas localmente. Capacidade é MW; geração horária ONS foi convertida para MWh/TWh; carga permanece em MWmed.",
        "",
        f"- A capacidade instalada operacional no SIGA soma **{total_capacity:,.1f} MW**.",
        f"- Fontes renováveis representam **{pct(renewable, total_capacity):,.1f}%** da capacidade operacional classificada.",
        f"- As maiores fontes por capacidade são: {', '.join(f'{k} ({v:,.1f} MW; {pct(v, total_capacity):,.1f}%)' for k, v in top(by_source))}.",
        f"- Os maiores estados por capacidade instalada são: {', '.join(f'{k} ({v:,.1f} MW)' for k, v in top(by_uf))}.",
        f"- A energia gerada no recorte ONS soma **{total_energy_mwh / 1_000_000:,.1f} TWh**, calculada por soma de MWh horários do subsistema SIN.",
        f"- A geração média no período é **{(total_energy_mwh / len({r.get('DataHora') for r in generation if r.get('DataHora')})) if generation else 0:,.1f} MWmed**.",
        f"- As maiores fontes por energia efetiva são: {', '.join(f'{k} ({v / 1_000_000:,.1f} TWh; {pct(v, total_energy_mwh):,.1f}%)' for k, v in top(energy_by_source))}.",
        f"- A carga média do SIN é **{avg_load:,.1f} MWmed**.",
        f"- A carga máxima do recorte é **{peak_value:,.1f} MWmed**, registrada em **{peak.get('DataHora', 'não informado')}**.",
        f"- A MMGD agregada soma **{total_mmgd:,.1f} MW** em **{systems:,} sistemas**.",
        f"- Os maiores estados em MMGD são: {', '.join(f'{k} ({v:,.1f} MW)' for k, v in top(mmgd_uf))}.",
        f"- A distribuição por fonte da MMGD é dominada por: {', '.join(f'{k} ({v:,.1f} MW)' for k, v in top(mmgd_source))}.",
        f"- A relação MMGD/capacidade operacional centralizada é **{pct(total_mmgd, total_capacity):,.1f}%**, útil para discutir descentralização da oferta.",
        "- Capacidade instalada e energia gerada não precisam ter a mesma participação por fonte: disponibilidade, despacho, intermitência, hidrologia e custo variável mudam a produção efetiva.",
        "- Solar e eólica aparecem melhor quando capacidade e energia são analisadas lado a lado, porque potência instalada não equivale a geração firme.",
        "- A linha SIN do ONS foi usada como referência principal para evitar dupla contagem com os subsistemas.",
        "- O painel separa capacidade centralizada, MMGD, geração e carga para evitar misturar grandezas físicas diferentes.",
        "- PLD é mantido como preço em R$/MWh, servindo para análise econômica sem contaminar métricas físicas.",
        "- O arquivo `reports/duplicidades_siga.csv` registra a auditoria dos núcleos CEG; a chave do fato operacional usa `CodCEG`.",
    ]
    if pld:
        pld_values = [to_float(row.get("PLD_Medio_R$/MWh")) or 0 for row in pld]
        lines.append(f"- O PLD mensal processado varia de **R$ {min(pld_values):,.2f}/MWh** a **R$ {max(pld_values):,.2f}/MWh** no recorte disponível.")

    lines.extend([
        "",
        "## Leitura para Entrevista",
        "",
        "A principal defesa técnica do projeto é a disciplina de unidades: MW mede potência/capacidade, MWmed mede potência média em uma janela, MWh/TWh mede energia acumulada e R$/MWh mede preço. Essa separação evita conclusões incorretas e demonstra domínio tanto do setor elétrico quanto de modelagem analítica.",
    ])
    (ROOT / "docs/insights.md").write_text("\n".join(lines), encoding="utf-8")
    print("[OK] insights")


if __name__ == "__main__":
    main()
