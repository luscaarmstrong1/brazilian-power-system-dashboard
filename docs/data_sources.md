# Data Sources

Extraction date: 2026-09-08.

## ANEEL SIGA

- Name: SIGA - Sistema de Informações de Geração da ANEEL
- Agency: Agência Nacional de Energia Elétrica
- URL: https://dadosabertos.aneel.gov.br/pt_BR/dataset/siga-sistema-de-informacoes-de-geracao-da-aneel
- Access method: CKAN API and CSV resource download
- Format: CSV
- Observed update: 2026-09-08 07:40 BRT on the official portal
- Frequency: monthly and daily
- Scope: national generation assets in several project phases
- Unit: source power fields in kW; modeled as MW
- License: Open Data Commons Open Database License (ODbL)
- Transformations: source classification, kW to MW, UF/region mapping, date parsing

## ANEEL MMGD

- Name: Relação de empreendimentos de Mini e Micro Geração Distribuída
- Agency: Agência Nacional de Energia Elétrica
- URL: https://dadosabertos.aneel.gov.br/dataset/relacao-de-empreendimentos-de-geracao-distribuida
- Access method: CKAN API, Datastore extract by default; full CSV optional
- Format: CSV
- Observed update: 2026-09-08 on resource pages
- Scope: national MMGD connections
- Unit: installed power in kW where supplied; modeled as MW
- License: Open Data Commons Open Database License (ODbL)
- Transformations: aggregation by year, UF, source and consumer class

## ONS Energy Balance by Subsystem

- Name: Balanço de Energia nos Subsistemas
- Agency: Operador Nacional do Sistema Elétrico
- URL: https://dados.ons.org.br/dataset/balanco-energia-subsistema
- Access method: CKAN API and CSV resources hosted by ONS/S3
- Format: CSV
- Scope: SIN subsystems
- Unit: generation and load in MWmed
- License: Creative Commons Attribution
- Transformations: source columns unpivoted to a generation fact table; load retained separately

## ONS Daily Load

- Name: Carga de Energia Diária
- Agency: Operador Nacional do Sistema Elétrico
- URL: https://dados.ons.org.br/dataset/carga-energia
- Access method: CKAN API and CSV resources
- Format: CSV
- Scope: SIN subsystems
- Unit: MWmed
- License: Creative Commons Attribution
- Note: ONS documents methodological changes through February 2021, March 2021-April 2023 and from 2023-04-29 with estimated MMGD incorporated.

## CCEE PLD

- Name: PLD_MEDIA_MENSAL
- Agency: Câmara de Comercialização de Energia Elétrica
- URL: https://dadosabertos.ccee.org.br/dataset/?tags=pld
- Access method: CKAN API when available
- Format: CSV
- Scope: submarket/month
- Unit: R$/MWh
- License: Creative Commons Attribution 4.0 on listed CCEE CSV resources
- Transformations: optional v1 module; failures are reported instead of backfilled with unofficial data
