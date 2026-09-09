from __future__ import annotations

import io
import json
import zipfile
from calendar import monthrange
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

from src.common import ROOT, first_present, iter_csv_rows_from_handle, read_csv_rows, to_float, write_csv
from src.source_mapping import classify_source


UF_TO_REGION = {
    "AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste", "PB": "Nordeste", "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste", "MS": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
}

SOURCE_PT = {
    "Hydro": "Hidrelétrica",
    "Small Hydro": "PCH/CGH",
    "Wind": "Eólica",
    "Solar": "Solar",
    "Biomass": "Biomassa",
    "Natural Gas": "Gás Natural",
    "Oil": "Óleo",
    "Coal": "Carvão",
    "Nuclear": "Nuclear",
    "Thermal Other": "Térmica Outras",
    "Other": "Outras",
}

CAPACITY_FIELDS = [
    "ID_Empreendimento", "ID_NucleoCEG", "Empreendimento", "FonteOriginal", "FonteAgrupada",
    "FonteExibicao", "Combustivel", "Renovavel", "Potencia_MW", "UF", "Regiao", "Municipio",
    "Latitude", "Longitude", "Situacao", "DataOperacao", "Agente", "TipoPotenciaUsada",
    "UnidadePotenciaOriginal", "UnidadePotenciaModelada", "FonteDados",
]

GENERATION_FIELDS = [
    "Data", "DataHora", "Subsistema", "FonteAgrupada", "FonteExibicao", "Geracao_MWmed",
    "Duracao_horas", "Energia_MWh", "Energia_GWh", "FonteDados",
]

LOAD_FIELDS = ["Data", "DataHora", "Subsistema", "Carga_MWmed", "FonteDados"]

LOAD_SIN_FIELDS = ["Data", "DataHora", "CargaSIN_MWmed", "SubsistemasConsiderados", "FonteDados"]

MMGD_FIELDS = [
    "Ano", "Mes", "AnoMes", "UF", "Regiao", "Municipio", "FonteAgrupada", "FonteExibicao",
    "ClasseConsumo", "Modalidade", "Potencia_MW", "QuantidadeSistemas", "PotenciaMedia_kW",
    "FonteDados",
]


def parse_date(value: str) -> str:
    text = (value or "").strip().replace("T", " ")[:19]
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%d/%m/%Y %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            pass
    return ""


def parse_datetime(value: str) -> str:
    text = (value or "").strip().replace("T", " ")[:19]
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
    return text


def parse_year_month(row: dict[str, str]) -> tuple[str, str, str]:
    period = str(first_present(row, ["AnmPeriodoReferencia", "MES_REFERENCIA", "MesReferencia", "Data"])).strip()
    if len(period) >= 7 and period[4] in {"-", "/"}:
        year, month = period[:4], period[5:7]
    elif len(period) >= 6 and period[:6].isdigit():
        year, month = period[:4], period[4:6]
    else:
        date = parse_date(str(first_present(row, ["DatConexao", "DatGeracaoConjuntoDados"])))
        year, month = (date[:4], date[5:7]) if date else ("", "")
    return year, month, f"{year}-{month}" if year and month else ""


def build_capacity() -> tuple[list[dict], list[dict]]:
    rows, _ = read_csv_rows(ROOT / "data/raw/aneel_siga.csv")
    all_facts = []
    sources = {}
    duplicate_tracker = defaultdict(list)
    for idx, row in enumerate(rows, start=1):
        source_original = str(first_present(row, ["SigTipoGeracao", "DscFonteCombustivel", "DscOrigemCombustivel", "Fonte"])).strip()
        fuel = str(first_present(row, ["DscFonteCombustivel", "DscCombustivel", "NomFonteCombustivel", "NomCombustivel"])).strip()
        cls = classify_source(source_original, fuel)
        power_kw = to_float(first_present(row, ["MdaPotenciaFiscalizadaKw", "MdaPotenciaOutorgadaKw", "PotenciaFiscalizadaKw"]))
        power_mw = (power_kw / 1000) if power_kw is not None else None
        uf = str(first_present(row, ["SigUFPrincipal", "SigUfPrincipal", "SigUF", "UF"])).upper()
        cod_ceg = str(first_present(row, ["CodCEG", "CodEmpreendimento", "CEG"])).strip()
        nucleo = str(first_present(row, ["IdeNucleoCEG"])).strip()
        enterprise_id = cod_ceg or nucleo or f"SIGA-{idx}"
        duplicate_tracker[nucleo].append(enterprise_id)
        fact = {
            "ID_Empreendimento": enterprise_id,
            "ID_NucleoCEG": nucleo,
            "Empreendimento": first_present(row, ["NomEmpreendimento", "NomeEmpreendimento", "NomUsina"]),
            "FonteOriginal": source_original,
            "FonteAgrupada": cls["FonteAgrupada"],
            "FonteExibicao": SOURCE_PT.get(str(cls["FonteAgrupada"]), str(cls["FonteAgrupada"])),
            "Combustivel": fuel,
            "Renovavel": "Sim" if cls["Renovavel"] else "Não",
            "Potencia_MW": round(power_mw, 6) if power_mw is not None else "",
            "UF": uf,
            "Regiao": UF_TO_REGION.get(uf, ""),
            "Municipio": first_present(row, ["NomMunicipio", "DscMuninicpios", "Municipio"]),
            "Latitude": first_present(row, ["NumCoordNEmpreendimento", "Latitude"]),
            "Longitude": first_present(row, ["NumCoordEEmpreendimento", "Longitude"]),
            "Situacao": first_present(row, ["DscFaseUsina", "DscSituacao", "Situacao"]),
            "DataOperacao": parse_date(str(first_present(row, ["DatEntradaOperacao", "DatInicioOperacao", "DatGeracaoConjuntoDados"]))),
            "Agente": first_present(row, ["NomAgente", "DscPropriRegimePariticipacao", "NomEmpresa", "Agente"]),
            "TipoPotenciaUsada": "Potência fiscalizada ANEEL",
            "UnidadePotenciaOriginal": "kW",
            "UnidadePotenciaModelada": "MW",
            "FonteDados": "ANEEL SIGA",
        }
        all_facts.append(fact)
        sources[source_original] = {
            "ID_Fonte": source_original or "Desconhecida",
            "FonteOriginal": source_original or "Desconhecida",
            "FonteAgrupada": cls["FonteAgrupada"],
            "FonteExibicao": SOURCE_PT.get(str(cls["FonteAgrupada"]), str(cls["FonteAgrupada"])),
            "Tecnologia": cls["Tecnologia"],
            "Renovavel": "Sim" if cls["Renovavel"] else "Não",
            "CategoriaPrincipal": cls["CategoriaPrincipal"],
            "Combustivel": fuel,
            "Observacao": "Classificação por regras documentadas em docs/source_classification.md",
        }
    operational_raw = [row for row in all_facts if "Oper" in str(row.get("Situacao", ""))]
    operational = []
    seen_operational_ids = set()
    duplicated_enterprises = []
    for row in operational_raw:
        enterprise_id = row.get("ID_Empreendimento")
        if enterprise_id in seen_operational_ids:
            duplicated_enterprises.append(row)
            continue
        seen_operational_ids.add(enterprise_id)
        operational.append(row)
    write_csv(ROOT / "data/processed/Fato_CapacidadeSIGA_TodosStatus.csv", all_facts, CAPACITY_FIELDS)
    write_csv(ROOT / "data/processed/Fato_CapacidadeInstalada.csv", operational, CAPACITY_FIELDS)
    dim_sources = list(sources.values())
    write_csv(ROOT / "data/processed/Dim_FonteEnergia.csv", dim_sources, list(dim_sources[0].keys()) if dim_sources else [])

    duplicated_nuclei = [
        {"ID_NucleoCEG": key, "QuantidadeCodCEG": len(set(values)), "CodCEG": ", ".join(sorted(set(values))[:8])}
        for key, values in duplicate_tracker.items()
        if key and len(set(values)) > 1
    ]
    write_csv(ROOT / "reports/duplicidades_siga.csv", duplicated_nuclei, ["ID_NucleoCEG", "QuantidadeCodCEG", "CodCEG"])
    write_csv(ROOT / "reports/duplicidades_operacionais_siga.csv", duplicated_enterprises, CAPACITY_FIELDS)
    return operational, dim_sources


def build_ons() -> tuple[list[dict], list[dict], list[dict]]:
    generation = []
    load = []
    load_by_datetime: dict[str, dict] = {}
    explicit_sin_load: dict[str, dict] = {}
    for path in sorted((ROOT / "data/raw").glob("ons_balanco_*.csv")):
        rows, _ = read_csv_rows(path)
        for row in rows:
            date_time = parse_datetime(str(first_present(row, ["din_instante", "DinInstante", "Data"])))
            date = parse_date(date_time)
            subsys = first_present(row, ["id_subsistema", "NomSubsistema", "nom_subsistema"])
            source_fields = [
                ("Hydro", ["val_gerhidraulica", "ValGeracaoHidraulica"]),
                ("Thermal Other", ["val_gertermica", "ValGeracaoTermica"]),
                ("Wind", ["val_gereolica", "ValGeracaoEolica"]),
                ("Solar", ["val_gersolar", "ValGeracaoSolar"]),
            ]
            for source, fields in source_fields:
                value = to_float(first_present(row, fields))
                if value is not None:
                    generation.append({
                        "Data": date,
                        "DataHora": date_time,
                        "Subsistema": subsys,
                        "FonteAgrupada": source,
                        "FonteExibicao": SOURCE_PT.get(source, source),
                        "Geracao_MWmed": round(value, 6),
                        "Duracao_horas": 1.0,
                        "Energia_MWh": round(value, 6),
                        "Energia_GWh": round(value / 1000, 9),
                        "FonteDados": "ONS Balanço de Energia por Subsistema",
                    })
            carga = to_float(first_present(row, ["val_carga", "ValCarga"]))
            if carga is not None:
                load.append({"Data": date, "DataHora": date_time, "Subsistema": subsys, "Carga_MWmed": round(carga, 6), "FonteDados": "ONS Balanço de Energia por Subsistema"})
                if str(subsys).upper() == "SIN":
                    explicit_sin_load[date_time] = {"Data": date, "DataHora": date_time, "CargaSIN_MWmed": carga, "Subsistemas": {"SIN"}}
                else:
                    bucket = load_by_datetime.setdefault(date_time, {"Data": date, "DataHora": date_time, "CargaSIN_MWmed": 0.0, "Subsistemas": set()})
                    bucket["CargaSIN_MWmed"] += carga
                    bucket["Subsistemas"].add(str(subsys))
    load_sin = []
    combined_load = {**load_by_datetime, **explicit_sin_load}
    for item in sorted(combined_load.values(), key=lambda x: x["DataHora"]):
        load_sin.append({
            "Data": item["Data"],
            "DataHora": item["DataHora"],
            "CargaSIN_MWmed": round(item["CargaSIN_MWmed"], 6),
            "SubsistemasConsiderados": len(item["Subsistemas"]),
            "FonteDados": "ONS Balanço de Energia por Subsistema",
        })
    write_csv(ROOT / "data/processed/Fato_Geracao.csv", generation, GENERATION_FIELDS)
    write_csv(ROOT / "data/processed/Fato_Carga.csv", load, LOAD_FIELDS)
    write_csv(ROOT / "data/processed/Fato_CargaSIN.csv", load_sin, LOAD_SIN_FIELDS)
    return generation, load, load_sin


def iter_mmgd_rows() -> Iterable[dict[str, str]]:
    zip_path = ROOT / "data/raw/aneel_mmgd_full.zip"
    if zip_path.exists():
        with zipfile.ZipFile(zip_path) as archive:
            member = next((name for name in archive.namelist() if name.lower().endswith(".csv")), None)
            if member is None:
                return
            with archive.open(member) as raw:
                text = io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace", newline="")
                yield from iter_csv_rows_from_handle(text)
        return
    rows, _ = read_csv_rows(ROOT / "data/raw/aneel_mmgd.csv")
    yield from rows


def select_col(frame: pd.DataFrame, candidates: list[str], default: str = "") -> pd.Series:
    lower = {col.lower(): col for col in frame.columns}
    for candidate in candidates:
        key = lower.get(candidate.lower())
        if key is not None:
            return frame[key].fillna("").astype(str)
    return pd.Series([default] * len(frame), index=frame.index, dtype="string")


def mmgd_chunks() -> Iterable[pd.DataFrame]:
    zip_path = ROOT / "data/raw/aneel_mmgd_full.zip"
    if zip_path.exists():
        for encoding in ("utf-8-sig", "latin1"):
            try:
                yield from pd.read_csv(zip_path, sep=";", dtype=str, chunksize=250_000, encoding=encoding, compression="zip", low_memory=False)
                return
            except UnicodeDecodeError:
                continue
    else:
        yield from pd.read_csv(ROOT / "data/raw/aneel_mmgd.csv", dtype=str, chunksize=250_000, low_memory=False)


def build_mmgd() -> list[dict]:
    partials = []
    source_cache: dict[str, dict[str, object]] = {}
    for chunk in mmgd_chunks():
        uf = select_col(chunk, ["SigUF", "SigUfConsumidor", "UF"]).str.upper().str.strip()
        period = select_col(chunk, ["AnmPeriodoReferencia"]).str.strip()
        fallback_date = select_col(chunk, ["DatGeracaoConjuntoDados", "DatConexao"]).str[:10]
        year = period.str[:4].where(period.str.len() >= 6, fallback_date.str[:4])
        month = period.str[4:6].where(period.str[:6].str.isdigit(), fallback_date.str[5:7])
        year_month = year.fillna("") + "-" + month.fillna("")
        source_original = select_col(chunk, ["DscFonteGeracao", "DscFonte", "Fonte", "SigTipoGeracao"]).str.strip()
        for value in source_original.dropna().unique():
            if value not in source_cache:
                source_cache[value] = classify_source(str(value))
        grouped = source_original.map(lambda value: source_cache.get(str(value), classify_source(str(value)))["FonteAgrupada"])
        cls_consumo = select_col(chunk, ["DscClasseConsumo", "ClasseConsumo"], "Não informado").replace("", "Não informado")
        power_text = select_col(chunk, ["MdaPotenciaInstaladaKW", "MdaPotenciaInstalada", "PotenciaInstaladaKW"], "0")
        power_kw = pd.to_numeric(power_text.str.replace(".", "", regex=False).str.replace(",", ".", regex=False), errors="coerce").fillna(0)
        frame = pd.DataFrame({
            "Ano": year,
            "Mes": month,
            "AnoMes": year_month,
            "UF": uf,
            "FonteAgrupada": grouped,
            "ClasseConsumo": cls_consumo,
            "Potencia_MW": power_kw / 1000,
            "QuantidadeSistemas": 1,
        })
        partials.append(frame.groupby(["Ano", "Mes", "AnoMes", "UF", "FonteAgrupada", "ClasseConsumo"], dropna=False, as_index=False).agg({"Potencia_MW": "sum", "QuantidadeSistemas": "sum"}))
    if not partials:
        write_csv(ROOT / "data/processed/Fato_MMGD_Agregada.csv", [], MMGD_FIELDS)
        write_csv(ROOT / "data/processed/Fato_MMGD.csv", [], MMGD_FIELDS)
        return []
    grouped = pd.concat(partials, ignore_index=True).groupby(["Ano", "Mes", "AnoMes", "UF", "FonteAgrupada", "ClasseConsumo"], dropna=False, as_index=False).agg({"Potencia_MW": "sum", "QuantidadeSistemas": "sum"})
    facts = []
    for row in grouped.to_dict(orient="records"):
        source = str(row["FonteAgrupada"])
        qtd = int(row["QuantidadeSistemas"])
        potencia = float(row["Potencia_MW"])
        facts.append({
            "Ano": row["Ano"],
            "Mes": row["Mes"],
            "AnoMes": row["AnoMes"],
            "UF": row["UF"],
            "Regiao": UF_TO_REGION.get(str(row["UF"]), ""),
            "Municipio": "Todos",
            "FonteAgrupada": source,
            "FonteExibicao": SOURCE_PT.get(source, source),
            "ClasseConsumo": row["ClasseConsumo"] or "Não informado",
            "Modalidade": "Todas",
            "Potencia_MW": round(potencia, 6),
            "QuantidadeSistemas": qtd,
            "PotenciaMedia_kW": round((potencia * 1000) / qtd, 6) if qtd else 0,
            "FonteDados": "ANEEL MMGD",
        })
    facts.sort(key=lambda r: (r["Ano"], r["Mes"], r["UF"], r["FonteExibicao"], r["ClasseConsumo"]))
    write_csv(ROOT / "data/processed/Fato_MMGD_Agregada.csv", facts, MMGD_FIELDS)
    write_csv(ROOT / "data/processed/Fato_MMGD.csv", facts, MMGD_FIELDS)
    return facts


def build_pld() -> list[dict]:
    rows_out = []
    for path in sorted((ROOT / "data/raw").glob("ccee_pld_media_mensal*.csv")):
        rows, _ = read_csv_rows(path)
        for row in rows:
            year, month, year_month = parse_year_month(row)
            value = to_float(first_present(row, ["PLD_MEDIA_MES", "PldMediaMes", "PLD"]))
            submarket = first_present(row, ["SUBMERCADO", "Submercado"])
            if value is None or not year_month:
                continue
            rows_out.append({
                "Ano": year,
                "Mes": month,
                "AnoMes": year_month,
                "Submercado": submarket,
                "PLD_Medio_R$/MWh": round(value, 6),
                "FonteDados": "CCEE PLD média mensal",
            })
    write_csv(ROOT / "data/processed/Fato_PLD.csv", rows_out, ["Ano", "Mes", "AnoMes", "Submercado", "PLD_Medio_R$/MWh", "FonteDados"])
    return rows_out


def build_calendar(datasets: list[list[dict]]) -> None:
    dates = set()
    for dataset in datasets:
        for row in dataset:
            date = row.get("Data") or row.get("DataOperacao")
            if date:
                dates.add(date[:10])
    rows = []
    for date in sorted(dates):
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            continue
        rows.append({
            "Data": date,
            "Ano": dt.year,
            "Mes": dt.strftime("%m"),
            "NumeroMes": dt.month,
            "MesAno": dt.strftime("%Y-%m"),
            "Trimestre": f"T{((dt.month - 1) // 3) + 1}",
            "Semana": dt.isocalendar().week,
            "Dia": dt.day,
            "DiaSemana": dt.weekday() + 1,
            "AnoMes": f"{dt.year}{dt.month:02d}",
            "InicioMes": f"{dt.year}-{dt.month:02d}-01",
            "FimMes": f"{dt.year}-{dt.month:02d}-{monthrange(dt.year, dt.month)[1]:02d}",
        })
    write_csv(ROOT / "data/processed/Dim_Calendario.csv", rows, ["Data", "Ano", "Mes", "NumeroMes", "MesAno", "Trimestre", "Semana", "Dia", "DiaSemana", "AnoMes", "InicioMes", "FimMes"])


def build_dimensions(capacity: list[dict]) -> None:
    ufs = [{"UF": uf, "Regiao": UF_TO_REGION.get(uf, "")} for uf in sorted({r["UF"] for r in capacity if r.get("UF")})]
    write_csv(ROOT / "data/processed/Dim_UF.csv", ufs, ["UF", "Regiao"])
    status = [{"Situacao": s} for s in sorted({r["Situacao"] for r in capacity if r.get("Situacao")})]
    write_csv(ROOT / "data/processed/Dim_Situacao.csv", status, ["Situacao"])


def write_portfolio_outputs(capacity: list[dict], generation: list[dict], load_sin: list[dict], mmgd: list[dict], pld: list[dict]) -> None:
    portfolio = ROOT / "data/portfolio"
    portfolio.mkdir(parents=True, exist_ok=True)

    def aggregate(rows: list[dict], dims: list[str], metric: str) -> list[dict]:
        buckets = defaultdict(float)
        for row in rows:
            buckets[tuple(row.get(dim, "") for dim in dims)] += to_float(row.get(metric)) or 0
        out = []
        for key, value in buckets.items():
            item = {dim: key[idx] for idx, dim in enumerate(dims)}
            item[metric] = round(value, 6)
            out.append(item)
        return sorted(out, key=lambda r: tuple(r.get(dim, "") for dim in dims))

    write_csv(portfolio / "capacidade_por_fonte.csv", aggregate(capacity, ["FonteExibicao", "Renovavel"], "Potencia_MW"), ["FonteExibicao", "Renovavel", "Potencia_MW"])
    write_csv(portfolio / "capacidade_por_uf.csv", aggregate(capacity, ["UF", "Regiao"], "Potencia_MW"), ["UF", "Regiao", "Potencia_MW"])
    generation_sin = [row for row in generation if str(row.get("Subsistema", "")).upper() == "SIN"] or generation
    write_csv(portfolio / "geracao_por_fonte.csv", aggregate(generation_sin, ["FonteExibicao"], "Energia_MWh"), ["FonteExibicao", "Energia_MWh"])
    write_csv(portfolio / "geracao_mensal.csv", aggregate(generation_sin, ["Data", "FonteExibicao"], "Energia_MWh"), ["Data", "FonteExibicao", "Energia_MWh"])
    write_csv(portfolio / "carga_sin.csv", load_sin, LOAD_SIN_FIELDS)
    write_csv(portfolio / "mmgd_por_uf.csv", aggregate(mmgd, ["UF", "Regiao", "FonteExibicao"], "Potencia_MW"), ["UF", "Regiao", "FonteExibicao", "Potencia_MW"])
    write_csv(portfolio / "pld.csv", pld, ["Ano", "Mes", "AnoMes", "Submercado", "PLD_Medio_R$/MWh", "FonteDados"])

    metadata = {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "fontes": {
            "ANEEL SIGA": "https://dadosabertos.aneel.gov.br/pt_BR/dataset/siga-sistema-de-informacoes-de-geracao-da-aneel",
            "ANEEL MMGD": "https://dadosabertos.aneel.gov.br/dataset/relacao-de-empreendimentos-de-geracao-distribuida",
            "ONS Balanço": "https://dados.ons.org.br/dataset/balanco-energia-subsistema",
            "ONS Carga": "https://dados.ons.org.br/dataset/carga-energia",
            "CCEE PLD": "https://dadosabertos.ccee.org.br/dataset/pld_media_mensal",
        },
        "observacao_unidades": "MWmed foi convertido para Energia_MWh assumindo granularidade horária dos arquivos ONS. MWmed não é somado como energia.",
    }
    (portfolio / "data_freshness.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    outputs = ROOT.parent / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    (outputs / "data_freshness.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def build_kpis() -> None:
    capacity, _ = read_csv_rows(ROOT / "data/processed/Fato_CapacidadeInstalada.csv")
    generation_all, _ = read_csv_rows(ROOT / "data/processed/Fato_Geracao.csv")
    generation = [row for row in generation_all if str(row.get("Subsistema", "")).upper() == "SIN"] or generation_all
    load_sin, _ = read_csv_rows(ROOT / "data/processed/Fato_CargaSIN.csv")
    mmgd, _ = read_csv_rows(ROOT / "data/processed/Fato_MMGD.csv")
    total_capacity = sum(to_float(r.get("Potencia_MW")) or 0 for r in capacity)
    renewable_capacity = sum((to_float(r.get("Potencia_MW")) or 0) for r in capacity if r.get("Renovavel") == "Sim")
    total_energy_mwh = sum(to_float(r.get("Energia_MWh")) or 0 for r in generation)
    unique_hours = len({r.get("DataHora") for r in generation if r.get("DataHora")})
    avg_generation = total_energy_mwh / unique_hours if unique_hours else 0
    avg_load = sum(to_float(r.get("CargaSIN_MWmed")) or 0 for r in load_sin) / len(load_sin) if load_sin else 0
    peak_row = max(load_sin, key=lambda r: to_float(r.get("CargaSIN_MWmed")) or 0, default={})
    peak_load = to_float(peak_row.get("CargaSIN_MWmed")) or 0
    total_mmgd = sum(to_float(r.get("Potencia_MW")) or 0 for r in mmgd)
    systems_mmgd = sum(int(to_float(r.get("QuantidadeSistemas")) or 0) for r in mmgd)
    kpis = [
        {"Indicador": "Capacidade instalada operacional", "Valor": round(total_capacity, 3), "Unidade": "MW", "Escopo": "Brasil / ANEEL SIGA / fase Operação"},
        {"Indicador": "Capacidade renovável operacional", "Valor": round(renewable_capacity, 3), "Unidade": "MW", "Escopo": "Brasil / classificação documentada"},
        {"Indicador": "Participação renovável na capacidade", "Valor": round(renewable_capacity / total_capacity * 100, 3) if total_capacity else 0, "Unidade": "%", "Escopo": "Brasil / ANEEL SIGA"},
        {"Indicador": "Energia gerada no período ONS", "Valor": round(total_energy_mwh / 1_000_000, 3), "Unidade": "TWh", "Escopo": "SIN / ONS / soma de MWh horários"},
        {"Indicador": "Geração média no período", "Valor": round(avg_generation, 3), "Unidade": "MWmed", "Escopo": "SIN / ONS / energia dividida por horas"},
        {"Indicador": "Carga média SIN", "Valor": round(avg_load, 3), "Unidade": "MWmed", "Escopo": "SIN / ONS / soma dos subsistemas por hora"},
        {"Indicador": "Carga máxima SIN", "Valor": round(peak_load, 3), "Unidade": "MWmed", "Escopo": f"SIN / ONS / {peak_row.get('DataHora', '')}"},
        {"Indicador": "Capacidade MMGD agregada", "Valor": round(total_mmgd, 3), "Unidade": "MW", "Escopo": "Brasil / ANEEL MMGD"},
        {"Indicador": "Sistemas MMGD", "Valor": systems_mmgd, "Unidade": "sistemas", "Escopo": "Brasil / ANEEL MMGD"},
    ]
    write_csv(ROOT / "data/processed/kpi_snapshot.csv", kpis, ["Indicador", "Valor", "Unidade", "Escopo"])


def main() -> None:
    capacity, _ = build_capacity()
    generation, load, load_sin = build_ons()
    mmgd = build_mmgd()
    pld = build_pld()
    build_calendar([capacity, generation, load])
    build_dimensions(capacity)
    build_kpis()
    write_portfolio_outputs(capacity, generation, load_sin, mmgd, pld)
    metadata_files = sorted((ROOT / "data/raw").glob("metadata_*.json"))
    merged = []
    for path in metadata_files:
        merged.extend(json.loads(path.read_text(encoding="utf-8")))
    (ROOT / "data/raw/metadata.json").write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[OK] modelo dimensional corrigido")


if __name__ == "__main__":
    main()
