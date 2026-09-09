# Methodology

1. Sources: official ANEEL, ONS and CCEE portals are queried through CKAN APIs.
2. Extraction: CSV resources are downloaded or extracted from official Datastore endpoints with cache metadata.
3. Standardization: raw columns are mapped into stable analytical fields.
4. Classification: original source labels are preserved and grouped through documented rules.
5. Units: ANEEL kW fields are converted to MW; ONS MWmed values remain MWmed.
6. Time: dates are parsed to ISO format and linked to `Dim_Calendario`.
7. Geography: UF and region are modeled; coordinates are retained when official fields exist.
8. Model: separate fact tables are created for capacity, generation, load and MMGD.
9. KPIs: executive indicators are computed in processed snapshots and documented as DAX.
10. Visualization: Power BI pages are specified with cards, charts, maps, filters and drill-through behavior.
