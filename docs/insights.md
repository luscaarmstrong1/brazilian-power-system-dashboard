# Insights do Sistema Elétrico Brasileiro

Todos os achados abaixo usam bases oficiais processadas localmente. Capacidade é MW; geração horária ONS foi convertida para MWh/TWh; carga permanece em MWmed.

- A capacidade instalada operacional no SIGA soma **220,466.1 MW**.
- Fontes renováveis representam **76.6%** da capacidade operacional classificada.
- As maiores fontes por capacidade são: Hidrelétrica (103,235.1 MW; 46.8%), Eólica (34,936.7 MW; 15.8%), Solar (23,602.5 MW; 10.7%), Gás Natural (19,999.1 MW; 9.1%), Térmica Outras (18,185.9 MW; 8.2%).
- Os maiores estados por capacidade instalada são: SP (25,474.6 MW), MG (25,272.0 MW), PA (23,478.9 MW), BA (22,019.2 MW), PR (17,687.1 MW).
- A energia gerada no recorte ONS soma **3,730.8 TWh**, calculada por soma de MWh horários do subsistema SIN.
- A geração média no período é **74,915.3 MWmed**.
- As maiores fontes por energia efetiva são: Hidrelétrica (2,374.4 TWh; 63.6%), Eólica (541.2 TWh; 14.5%), Térmica Outras (520.0 TWh; 13.9%), Solar (295.2 TWh; 7.9%).
- A carga média do SIN é **74,682.7 MWmed**.
- A carga máxima do recorte é **106,148.7 MWmed**, registrada em **2025-02-26 14:00:00**.
- A MMGD agregada soma **54,385.8 MW** em **4,692,850 sistemas**.
- Os maiores estados em MMGD são: SP (7,594.5 MW), PR (6,894.5 MW), MG (6,205.2 MW), RS (3,879.3 MW), MT (3,183.4 MW).
- A distribuição por fonte da MMGD é dominada por: Solar (53,231.0 MW), Outras (989.3 MW), Biomassa (162.8 MW), Gás Natural (2.5 MW), Óleo (0.3 MW).
- A relação MMGD/capacidade operacional centralizada é **24.7%**, útil para discutir descentralização da oferta.
- Capacidade instalada e energia gerada não precisam ter a mesma participação por fonte: disponibilidade, despacho, intermitência, hidrologia e custo variável mudam a produção efetiva.
- Solar e eólica aparecem melhor quando capacidade e energia são analisadas lado a lado, porque potência instalada não equivale a geração firme.
- A linha SIN do ONS foi usada como referência principal para evitar dupla contagem com os subsistemas.
- O painel separa capacidade centralizada, MMGD, geração e carga para evitar misturar grandezas físicas diferentes.
- PLD é mantido como preço em R$/MWh, servindo para análise econômica sem contaminar métricas físicas.
- O arquivo `reports/duplicidades_siga.csv` registra a auditoria dos núcleos CEG; a chave do fato operacional usa `CodCEG`.
- O PLD mensal processado varia de **R$ 55.57/MWh** a **R$ 583.88/MWh** no recorte disponível.

## Leitura para Entrevista

A principal defesa técnica do projeto é a disciplina de unidades: MW mede potência/capacidade, MWmed mede potência média em uma janela, MWh/TWh mede energia acumulada e R$/MWh mede preço. Essa separação evita conclusões incorretas e demonstra domínio tanto do setor elétrico quanto de modelagem analítica.