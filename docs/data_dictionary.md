# Data Dictionary

| Table | Field | Type | Unit | Source | Description | Transformation |
|---|---|---|---|---|---|---|
| Fato_CapacidadeInstalada | Potencia_MW | decimal | MW | ANEEL SIGA | Installed capacity | Converted from kW |
| Fato_CapacidadeInstalada | FonteOriginal | text | n/a | ANEEL SIGA | Original source label | Preserved |
| Fato_CapacidadeInstalada | FonteAgrupada | text | n/a | Derived | Analytical source group | Rule-based classification |
| Fato_Geracao | Geracao_MWmed | decimal | MWmed | ONS | Effective generation by source/subsystem | Preserved unit |
| Fato_Carga | Carga_MWmed | decimal | MWmed | ONS | System load by subsystem | Preserved unit |
| Fato_MMGD | Potencia_MW | decimal | MW | ANEEL MMGD | Distributed generation installed power | Converted from kW when source field is kW |
| Fato_MMGD | QuantidadeSistemas | integer | systems | ANEEL MMGD | Count of records/systems in extract | Aggregated |
| Dim_Calendario | Data | date | n/a | Derived | Calendar date | Parsed from fact dates |
| Dim_FonteEnergia | Renovavel | boolean | n/a | Derived | Renewable flag | Documented classification |
| Dim_UF | Regiao | text | n/a | Derived | Brazilian macro-region | UF mapping |
