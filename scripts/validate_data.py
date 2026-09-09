from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from src.common import ROOT, read_csv_rows, to_float

VALID_UF = {"AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"}


def profile(path: Path) -> dict:
    rows, fields = read_csv_rows(path)
    missing = {f: sum(1 for r in rows if r.get(f, "") == "") for f in fields}
    return {"file": str(path.relative_to(ROOT)), "rows": len(rows), "columns": len(fields), "missing": missing}


def main() -> None:
    report = ["# Relatório de Qualidade dos Dados", "", "Gerado por `scripts/validate_data.py`.", ""]
    errors = []
    warnings = []

    for path in sorted((ROOT / "data/processed").glob("*.csv")):
        info = profile(path)
        report.append(f"## {info['file']}")
        report.append(f"- Linhas: {info['rows']}")
        report.append(f"- Colunas: {info['columns']}")
        fully_missing = [k for k, v in info["missing"].items() if info["rows"] and v == info["rows"]]
        if fully_missing:
            warnings.append(f"{info['file']}: colunas totalmente vazias: {', '.join(fully_missing)}")
        report.append("")

    capacity, _ = read_csv_rows(ROOT / "data/processed/Fato_CapacidadeInstalada.csv")
    ids = Counter(r.get("ID_Empreendimento") for r in capacity if r.get("ID_Empreendimento"))
    for row in capacity:
        power = to_float(row.get("Potencia_MW"))
        if power is not None and power < 0:
            errors.append(f"Capacidade instalada negativa: {row.get('ID_Empreendimento')}")
        uf = row.get("UF")
        if uf and uf not in VALID_UF:
            warnings.append(f"UF inválida ou não padronizada em capacidade: {uf}")
        if "Oper" not in str(row.get("Situacao", "")):
            errors.append(f"Fato_CapacidadeInstalada contém situação não operacional: {row.get('Situacao')}")
    duplicated = sum(1 for _, count in ids.items() if count > 1)
    if duplicated:
        errors.append(f"IDs CodCEG duplicados em capacidade operacional: {duplicated}")

    generation, _ = read_csv_rows(ROOT / "data/processed/Fato_Geracao.csv")
    for row in generation:
        mwmed = to_float(row.get("Geracao_MWmed"))
        hours = to_float(row.get("Duracao_horas"))
        mwh = to_float(row.get("Energia_MWh"))
        if mwmed is not None and mwmed < 0:
            errors.append(f"Geração MWmed negativa em {row.get('DataHora')}")
        if mwmed is not None and hours is not None and mwh is not None and abs((mwmed * hours) - mwh) > 0.01:
            errors.append(f"Conversão MWmed->MWh inconsistente em {row.get('DataHora')}")

    load, _ = read_csv_rows(ROOT / "data/processed/Fato_Carga.csv")
    load_sin, _ = read_csv_rows(ROOT / "data/processed/Fato_CargaSIN.csv")
    explicit_sin = {r["DataHora"]: to_float(r.get("Carga_MWmed")) or 0 for r in load if str(r.get("Subsistema", "")).upper() == "SIN"}
    subsystem_sum = defaultdict(float)
    for row in load:
        value = to_float(row.get("Carga_MWmed")) or 0
        if value < 0:
            errors.append(f"Carga MWmed negativa em {row.get('DataHora')}")
        if str(row.get("Subsistema", "")).upper() != "SIN":
            subsystem_sum[row.get("DataHora")] += value
    for row in load_sin:
        data_hora = row.get("DataHora")
        value = to_float(row.get("CargaSIN_MWmed")) or 0
        expected = explicit_sin.get(data_hora, subsystem_sum.get(data_hora, 0))
        if abs(value - expected) > 0.01:
            errors.append(f"Carga SIN inconsistente em {data_hora}: {value} vs {expected}")

    report.extend(["## Achados de Validação", ""])
    report.append("### Erros")
    report.extend([f"- {e}" for e in errors] or ["- Nenhum"])
    report.append("")
    report.append("### Avisos")
    report.extend([f"- {w}" for w in warnings] or ["- Nenhum"])
    report.append("")
    report.append("## Guardrails de Unidade")
    report.append("- Capacidade instalada é modelada em MW após conversão dos campos em kW da ANEEL.")
    report.append("- Geração ONS em MWmed foi convertida para Energia_MWh usando duração horária; totais usam MWh/TWh, não soma bruta de MWmed.")
    report.append("- Carga SIN usa a linha SIN oficial do ONS quando ela existe; a soma dos subsistemas é apenas fallback.")
    report.append("- MMGD é capacidade instalada em MW e não é somada com geração horária.")
    report.append("- PLD fica em R$/MWh e não é combinado com grandezas físicas.")
    (ROOT / "reports/data_quality_report.md").write_text("\n".join(report), encoding="utf-8")
    (ROOT / "RELATORIO_VALIDACAO.md").write_text("\n".join(report), encoding="utf-8")
    print("[OK] relatório de qualidade")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
