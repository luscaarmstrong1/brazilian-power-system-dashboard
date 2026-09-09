# Assumptions

- SIGA power fields ending in `Kw` are treated as kW and converted to MW.
- ONS balance generation and load are MWmed as described by ONS.
- MMGD is a separate module and is not merged into centralized SIGA capacity totals.
- Default MMGD extraction may be limited by `cache.max_mmgd_records` to keep the pipeline practical on a portfolio machine.
- PLD is optional; no unofficial replacement is used when the CCEE API/resource cannot be resolved.
