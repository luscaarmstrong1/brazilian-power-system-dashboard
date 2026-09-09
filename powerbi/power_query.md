# Power Query

Import CSV files from `data/processed/`:

- `Fato_CapacidadeInstalada.csv`
- `Fato_Geracao.csv`
- `Fato_Carga.csv`
- `Fato_MMGD.csv`
- `Dim_Calendario.csv`
- `Dim_FonteEnergia.csv`
- `Dim_UF.csv`
- `Dim_Situacao.csv`
- `kpi_snapshot.csv`

Recommended steps:

1. Use `Folder.Files` or individual CSV connectors.
2. Set `Potencia_MW`, `Geracao_MWmed`, `Carga_MWmed` and `PotenciaMedia_kW` as decimal numbers.
3. Set `Data` and `DataOperacao` as date.
4. Keep source units in field names.
5. Merge dimensions only in the semantic model; do not flatten all facts into one table.
6. Relate `Dim_FonteEnergia[FonteAgrupada]` to fact source fields where applicable.
7. Relate `Dim_UF[UF]` to capacity and MMGD facts.
8. Relate `Dim_Calendario[Data]` to generation/load dates and use an inactive relationship to capacity operation date if needed.

Example M pattern:

```powerquery
let
    Source = Csv.Document(File.Contents("data/processed/Fato_CapacidadeInstalada.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {{"Potencia_MW", type number}, {"DataOperacao", type date}, {"UF", type text}, {"FonteAgrupada", type text}})
in
    Typed
```
