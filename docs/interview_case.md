# Interview Case

1. Problem: transform official power-sector data into decision-ready analytics.
2. Sources: ANEEL SIGA, ANEEL MMGD, ONS subsystem balance/load and optional CCEE PLD.
3. MW vs MWh: MW is power; MWh is energy over time.
4. Capacity vs generation: capacity is rated capability; generation is effective production.
5. Brazil vs SIN: national ANEEL scope differs from ONS SIN operational scope.
6. Source classification: original labels are preserved and grouped through documented rules.
7. Data model: star schema with separate facts and shared dimensions.
8. Multiple facts: capacity, generation, load, MMGD and PLD have different grains and units.
9. MMGD: modeled separately by year, UF, source and consumer class.
10. Granularity: each fact keeps its natural grain; comparisons use aligned dimensions only.
11. Unit controls: validation and DAX documentation prevent MW, MWmed, MWh and R$/MWh mixing.
12. Insights: generated from processed data in `docs/insights.md`.
13. Sector use: supports strategic views of matrix, geography, renewables and load.
14. Limitations: public data latency, optional large MMGD extract, no fake PBIX generation.
15. V2: regional interchanges, reservoirs, ENA, deeper PLD, transmission, forecasting, curtailment and hosting capacity.
