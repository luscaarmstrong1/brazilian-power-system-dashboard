# Dashboard Analítico do Sistema Elétrico Brasileiro
### *Brazilian Power System Analytics Dashboard*

[![Simulador Online](https://img.shields.io/badge/Simulador_Interativo-GitHub_Pages-D3A15C?style=for-the-badge&logo=github)](https://luscaarmstrong1.github.io/brazilian-power-system-dashboard/)
[![Portfólio Lucas Santos](https://img.shields.io/badge/Portf%C3%B3lio-Lucas_Santos-071827?style=for-the-badge&logo=vercel)](https://lucas-santos-portfolio-zeta.vercel.app/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Lucas_Silva_Santos-102B42?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/lucasssantos1/)
[![Python](https://img.shields.io/badge/Python-Engenharia_%26_Dados-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/luscaarmstrong1/brazilian-power-system-dashboard)

> **Camada 03 • Ecossistema de Engenharia, Energia, Dados & Automação**
> Análise integrada do SIN (ONS & ANEEL): capacidade instalada (SIGA), balanço de geração e carga por subsistema, expansão renovável e geração distribuída (MMGD).

---

## Acesse o Simulador Interativo e Demonstração Online

- **Simulador Paramétrico Web (GitHub Pages):** [https://luscaarmstrong1.github.io/brazilian-power-system-dashboard/](https://luscaarmstrong1.github.io/brazilian-power-system-dashboard/)
- **Vitrine no Portfólio Principal:** [https://lucas-santos-portfolio-zeta.vercel.app/#arquitetura](https://lucas-santos-portfolio-zeta.vercel.app/#arquitetura)

---

## Visão Geral e Problema de Engenharia

Plataforma analítica do Sistema Interligado Nacional (SIN): capacidade instalada (SIGA/ANEEL), geração e carga por subsistema (ONS), expansão solar/eólica e geração distribuída (MMGD) com Python, Streamlit e Power BI.

### Indicadores-Chave do Projeto (Caso-Base)

| Indicador Técnico | Resultado / Escopo | Detalhamento de Engenharia |
| :--- | :--- | :--- |
| **Matriz Elétrica SIN** | `200+ GW` | Capacidade fiscalizada SIGA/ANEEL |
| **Subsistemas ONS** | `SE/CO • S • NE • N` | Balanço energético e intercâmbio |
| **Expansão Renovável** | `> 88% Limpa` | Hídrica, Eólica, Solar e Biomassa |
| **Geração Distribuída** | `MMGD Nacional` | Evolução estadual e por classe |

---

## Arquitetura do Sistema e Fluxo de Modelagem

1. **Etapa 01:** Coleta e Padronização de Dados Públicos (Séries históricas ONS, SIGA/ANEEL e MMGD)
2. **Etapa 02:** Engenharia de Dados & Separação de Grandezas (Distinção rigorosa entre MW instalado, MWmed e MWh)
3. **Etapa 03:** Modelagem Dimensional Star Schema (Tabelas fato de geração/carga e dimensões geográficas e energéticas)
4. **Etapa 04:** Visualização Executiva em Streamlit & Power BI (Análise de sazonalidade, rampa horária e expansão)

---

## Fundamentação Física, Matemática e Regulatória

### 1. Fator de Capacidade Efetivo por Fonte
```text
FC = Geração_Média(MWmed) / Capacidade_Instalada(MW)
```

### 2. Balanço Energético por Subsistema SIN
```text
Carga_SIN(t) = G_Hidr(t) + G_Eól(t) + G_Sol(t) + G_Term(t) ± Intercâmbio(t)
```

### 3. Carga Líquida (Efeito Pato / Duck Curve)
```text
Carga_Líquida(t) = Carga_Global(t) - [G_Solar_Centralizada(t) + G_MMGD(t)]
```

---

## Painéis Analíticos e Evidências Visuais

### Visão Geral da Matriz Elétrica Brasileira (SIN)
![Visão Geral da Matriz Elétrica Brasileira (SIN)](assets/screenshots/overview.png)

### Despacho e Geração por Fonte Energética
![Despacho e Geração por Fonte Energética](assets/screenshots/generation.png)

### Curva de Carga e Demanda por Subsistema
![Curva de Carga e Demanda por Subsistema](assets/screenshots/load.png)

### Participação Renovável e Complementaridade Eólica-Solar
![Participação Renovável e Complementaridade Eólica-Solar](assets/screenshots/renewables.png)

---

## Como Executar Localmente

```bash
# 1. Clone o repositório
git clone https://github.com/luscaarmstrong1/brazilian-power-system-dashboard.git
cd brazilian-power-system-dashboard

# 2. Instale as dependências e execute a suíte analítica
pip install -r requirements.txt
pytest
streamlit run app.py
```

> **Nota Técnica:** Este projeto utiliza modelagem determinística auditável e séries sintéticas estruturadas para demonstração de arquitetura de engenharia elétrica, ciência de dados e tomada de decisão técnico-econômica. Não substitui projeto executivo, parecer de acesso da concessionária ou emissão de ART específica de campo.

---

## Autor e Responsável Técnico

**Lucas Silva Santos**
*Engenheiro Eletricista & Gerente de Projetos*
Energia • Dados • Inteligência Artificial • Automação • São João da Boa Vista, SP • Itajubá, MG

- **Portfólio:** [https://lucas-santos-portfolio-zeta.vercel.app/](https://lucas-santos-portfolio-zeta.vercel.app/)
- **LinkedIn:** [linkedin.com/in/lucasssantos1](https://www.linkedin.com/in/lucasssantos1/)
- **GitHub:** [@luscaarmstrong1](https://github.com/luscaarmstrong1)
