# Data Model

## Fact Tables

- `Fato_CapacidadeInstalada`: one row per SIGA undertaking/generation asset record.
- `Fato_Geracao`: one row per date/time, subsystem and generation source from ONS balance.
- `Fato_Carga`: one row per date/time and subsystem from ONS balance.
- `Fato_MMGD`: aggregated MMGD rows by year, UF, source and consumer class.
- `Fato_PLD`: optional monthly PLD by submarket if the CCEE extractor resolves the resource.

## Dimensions

- `Dim_Calendario`
- `Dim_FonteEnergia`
- `Dim_UF`
- `Dim_Situacao`
- `Dim_Subsistema` can be created in Power BI from distinct ONS subsystem values.

## Relationships

- Calendar to generation/load by `Data`.
- Calendar to capacity by `DataOperacao`, preferably inactive unless analyzing expansion.
- Source dimension to capacity/generation/MMGD by `FonteAgrupada`.
- UF dimension to capacity/MMGD by `UF`.
- Situation dimension to capacity by `Situacao`.

This design intentionally avoids one giant fact table because the measures have different grains, units and scopes.
