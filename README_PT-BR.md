# Dashboard Analítico do Sistema Elétrico Brasileiro

Projeto de portfólio em Engenharia Elétrica, Sistemas de Potência, Power BI, Python e Data Analytics.

## Visão Geral

O projeto constrói uma plataforma analítica reproduzível para responder perguntas sobre capacidade instalada, geração efetiva, carga do SIN, geração distribuída, expansão renovável e distribuição geográfica do sistema elétrico brasileiro.

## Brasil ≠ Necessariamente SIN

Indicadores nacionais da ANEEL, como SIGA e MMGD, representam bases de abrangência nacional. Indicadores de geração e carga do ONS representam o Sistema Interligado Nacional (SIN). O dashboard identifica o escopo de cada métrica para evitar interpretações incorretas.

## Como Executar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/update_all.py
streamlit run app.py
```

## Entregáveis

- Pipeline de extração, transformação e validação.
- Modelo dimensional com múltiplas tabelas fato.
- Medidas DAX documentadas.
- Power Query documentado.
- Tema JSON para Power BI.
- Mockups de 10 páginas.
- Documentação para GitHub, LinkedIn, currículo e entrevista.

## Unidades

Capacidade instalada é MW. Geração e carga do ONS são MWmed. Energia acumulada deve ser MWh, GWh ou TWh apenas quando houver conversão temporal documentada. PLD é R$/MWh.
