# DAX Measures

## [Capacidade Instalada MW]

```DAX
Capacidade Instalada MW = SUM(Fato_CapacidadeInstalada[Potencia_MW])
```

Description: total installed capacity. Unit: MW. Source: ANEEL SIGA.

## [Capacidade Instalada GW]

```DAX
Capacidade Instalada GW = DIVIDE([Capacidade Instalada MW], 1000)
```

Description: total installed capacity in GW. Unit: GW.

## [Capacidade Renovável MW]

```DAX
Capacidade Renovável MW =
CALCULATE(
    [Capacidade Instalada MW],
    Dim_FonteEnergia[Renovavel] = TRUE()
)
```

Description: installed capacity classified as renewable. Unit: MW.

## [% Capacidade Renovável]

```DAX
% Capacidade Renovável = DIVIDE([Capacidade Renovável MW], [Capacidade Instalada MW])
```

Description: renewable share of installed capacity. Unit: percent.

## [Capacidade Solar MW]

```DAX
Capacidade Solar MW =
CALCULATE([Capacidade Instalada MW], Dim_FonteEnergia[FonteAgrupada] = "Solar")
```

## [Capacidade Eólica MW]

```DAX
Capacidade Eólica MW =
CALCULATE([Capacidade Instalada MW], Dim_FonteEnergia[FonteAgrupada] = "Wind")
```

## [Capacidade Hidráulica MW]

```DAX
Capacidade Hidráulica MW =
CALCULATE([Capacidade Instalada MW], Dim_FonteEnergia[FonteAgrupada] IN {"Hydro", "Small Hydro"})
```

## [Capacidade Térmica MW]

```DAX
Capacidade Térmica MW =
CALCULATE([Capacidade Instalada MW], Dim_FonteEnergia[Tecnologia] = "Thermal")
```

## [Potência MMGD MW]

```DAX
Potência MMGD MW = SUM(Fato_MMGD[Potencia_MW])
```

Unit: MW. Source: ANEEL MMGD.

## [Quantidade MMGD]

```DAX
Quantidade MMGD = SUM(Fato_MMGD[QuantidadeSistemas])
```

Unit: systems.

## [Geração Total]

```DAX
Geração Total = SUM(Fato_Geracao[Geracao_MWmed])
```

Unit: MWmed records. Do not add to MW capacity.

## [% Geração por Fonte]

```DAX
% Geração por Fonte =
DIVIDE(
    [Geração Total],
    CALCULATE([Geração Total], ALL(Dim_FonteEnergia[FonteAgrupada]))
)
```

## [Carga Média]

```DAX
Carga Média = AVERAGE(Fato_Carga[Carga_MWmed])
```

Unit: MWmed. Scope: SIN.

## [Pico de Carga]

```DAX
Pico de Carga = MAX(Fato_Carga[Carga_MWmed])
```

Unit: MWmed. Scope: SIN.

## [Capacidade Adicionada Ano]

```DAX
Capacidade Adicionada Ano =
CALCULATE(
    [Capacidade Instalada MW],
    USERELATIONSHIP(Dim_Calendario[Data], Fato_CapacidadeInstalada[DataOperacao])
)
```

## [Crescimento YoY]

```DAX
Crescimento YoY =
VAR Atual = [Capacidade Instalada MW]
VAR Anterior =
    CALCULATE(
        [Capacidade Instalada MW],
        SAMEPERIODLASTYEAR(Dim_Calendario[Data])
    )
RETURN DIVIDE(Atual - Anterior, Anterior)
```

## [CAGR]

```DAX
CAGR =
VAR ValorInicial =
    CALCULATE([Capacidade Instalada MW], FIRSTDATE(Dim_Calendario[Data]))
VAR ValorFinal =
    CALCULATE([Capacidade Instalada MW], LASTDATE(Dim_Calendario[Data]))
VAR Anos =
    DIVIDE(DATEDIFF(FIRSTDATE(Dim_Calendario[Data]), LASTDATE(Dim_Calendario[Data]), DAY), 365.25)
RETURN
    IF(Anos > 0 && ValorInicial > 0, POWER(DIVIDE(ValorFinal, ValorInicial), DIVIDE(1, Anos)) - 1)
```
