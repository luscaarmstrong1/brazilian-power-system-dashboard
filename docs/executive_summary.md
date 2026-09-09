# Brazilian Power System Snapshot

This project combines official public datasets to describe the Brazilian electricity system through installed capacity, effective SIN generation, SIN load, distributed generation and market indicators.

## Generation Mix

ANEEL SIGA provides the installed capacity view by project/source. ONS provides the effective generation view in MWmed.

## Renewable Expansion

Solar, wind, hydro, small hydro and biomass are tracked with an explicit renewable classification.

## Distributed Generation

MMGD is modeled as its own fact table because consumer-unit distributed generation has different meaning, scale and granularity than centralized generation.

## System Load

Load is analyzed using ONS SIN datasets and labeled as SIN, not automatically as Brazil.

## Geographic Concentration

UF and region fields support maps, rankings and drill-through pages.

## Key Trends

Run `python scripts/update_all.py` to refresh official data and regenerate quantified insights in `docs/insights.md`.
