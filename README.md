# Brazilian Power System Analytics Dashboard

Power Systems • Electrical Engineering • Energy Analytics • Power BI • Python

## Overview

This portfolio project builds a reproducible analytics platform for the Brazilian power system using official public datasets. It separates installed capacity, effective generation, system load, distributed generation and market prices so that MW, MWmed, MWh and R$/MWh are never mixed silently.

## Business / Engineering Question

How is Brazil's electricity system structured, where is capacity located, what is effectively generated in the SIN, how does load behave and how are renewables and distributed generation changing the system?

## Dashboard Preview

Mockups are available in `assets/mockups/` and screenshots in `assets/screenshots/`.

## Brazilian Power System

Brazil is not always the same analytical scope as the SIN. ANEEL capacity and MMGD datasets are national datasets. ONS generation and load datasets refer to the Sistema Interligado Nacional (SIN), according to ONS dataset descriptions. The dashboard labels each KPI with its scope.

## Data Sources

- ANEEL SIGA: installed generation capacity and plant metadata.
- ANEEL MMGD: micro and mini distributed generation connections.
- ONS Energy Balance by Subsystem: hourly generation and load in MWmed by subsystem.
- ONS Daily Load: daily load in MWmed by subsystem.
- CCEE PLD: monthly average PLD when available through the official CKAN portal.

## Generation Capacity

Installed capacity is modeled from ANEEL SIGA. The source field is classified into a documented grouped source dimension without changing the original source label.

## Electricity Generation

Effective generation is modeled from ONS hourly subsystem balance. Values remain in MWmed and are not combined with MW installed capacity.

## System Load

Load is modeled from ONS balance and daily load datasets. The SIN scope is explicit.

## Distributed Generation

MMGD is modeled separately from centralized generation. The default extractor uses a configurable official CKAN Datastore extract to avoid repeatedly downloading the full large file.

## Renewable Energy

Renewable classification is defined in `docs/source_classification.md`. Nuclear is treated as non-renewable low-carbon, not renewable.

## Geographic Analysis

The model includes UF, region, municipality and coordinates when present in official source fields.

## Data Architecture

The project uses a star schema with multiple fact tables:

- `Fato_CapacidadeInstalada`
- `Fato_Geracao`
- `Fato_Carga`
- `Fato_MMGD`
- `Dim_Calendario`
- `Dim_FonteEnergia`
- `Dim_UF`
- `Dim_Situacao`

## Technologies

Python, CSV/Parquet-ready pipeline, Power BI DAX/Power Query specifications, Streamlit/Plotly-ready web app and pytest tests.

## Key Metrics

Installed capacity, renewable capacity share, solar/wind/hydro/thermal capacity, MMGD capacity and systems, ONS generation by source, average SIN load and peak SIN load.

## Insights

Generated insights are written to `docs/insights.md` after `python scripts/update_all.py` runs.

## How to Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/update_all.py
streamlit run app.py
```

## Data Update

Run:

```bash
python scripts/update_all.py
```

Set `cache.force_download: true` to refresh cached downloads. Set `cache.max_mmgd_records: 0` to download the full ANEEL MMGD CSV.

## Limitations

The repository does not create a fake PBIX. It provides the processed datasets, Power Query, DAX, theme, model and dashboard specification needed to assemble a native Power BI report.

## Disclaimer

This is an analytical portfolio project based on public official data. It is not an operational planning, dispatch or regulatory decision system.

## Author

Electrical Engineering and Energy Analytics portfolio project.
