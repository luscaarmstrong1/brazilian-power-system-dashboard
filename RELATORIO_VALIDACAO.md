# Relatório de Qualidade dos Dados

Gerado por `scripts/validate_data.py`.

## data\processed\Dim_Calendario.csv
- Linhas: 4947
- Colunas: 12

## data\processed\Dim_FonteEnergia.csv
- Linhas: 7
- Colunas: 9

## data\processed\Dim_Situacao.csv
- Linhas: 1
- Colunas: 1

## data\processed\Dim_UF.csv
- Linhas: 27
- Colunas: 2

## data\processed\Fato_CapacidadeInstalada.csv
- Linhas: 22819
- Colunas: 21

## data\processed\Fato_CapacidadeSIGA_TodosStatus.csv
- Linhas: 25133
- Colunas: 21

## data\processed\Fato_Carga.csv
- Linhas: 249000
- Colunas: 5

## data\processed\Fato_CargaSIN.csv
- Linhas: 49800
- Colunas: 5

## data\processed\Fato_Geracao.csv
- Linhas: 996000
- Colunas: 10

## data\processed\Fato_MMGD.csv
- Linhas: 326
- Colunas: 14

## data\processed\Fato_MMGD_Agregada.csv
- Linhas: 326
- Colunas: 14

## data\processed\Fato_PLD.csv
- Linhas: 272
- Colunas: 6

## data\processed\kpi_snapshot.csv
- Linhas: 9
- Colunas: 4

## Achados de Validação

### Erros
- Nenhum

### Avisos
- Nenhum

## Guardrails de Unidade
- Capacidade instalada é modelada em MW após conversão dos campos em kW da ANEEL.
- Geração ONS em MWmed foi convertida para Energia_MWh usando duração horária; totais usam MWh/TWh, não soma bruta de MWmed.
- Carga SIN usa a linha SIN oficial do ONS quando ela existe; a soma dos subsistemas é apenas fallback.
- MMGD é capacidade instalada em MW e não é somada com geração horária.
- PLD fica em R$/MWh e não é combinado com grandezas físicas.