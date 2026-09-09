SOURCE_RULES = [
    ("HIDRO", "Hydro", "Hydraulic", True, "Renewable"),
    ("UHE", "Hydro", "Hydraulic", True, "Renewable"),
    ("PCH", "Small Hydro", "Hydraulic", True, "Renewable"),
    ("CGH", "Small Hydro", "Hydraulic", True, "Renewable"),
    ("EOL", "Wind", "Wind", True, "Renewable"),
    ("EOLICA", "Wind", "Wind", True, "Renewable"),
    ("UFV", "Solar", "Solar photovoltaic", True, "Renewable"),
    ("SOLAR", "Solar", "Solar photovoltaic", True, "Renewable"),
    ("BIO", "Biomass", "Thermal renewable", True, "Renewable"),
    ("BIOMASSA", "Biomass", "Thermal renewable", True, "Renewable"),
    ("GAS", "Natural Gas", "Thermal", False, "Fossil"),
    ("OLEO", "Oil", "Thermal", False, "Fossil"),
    ("PETROLEO", "Oil", "Thermal", False, "Fossil"),
    ("CARVAO", "Coal", "Thermal", False, "Fossil"),
    ("NUCLEAR", "Nuclear", "Nuclear", False, "Non-renewable low-carbon"),
    ("UTN", "Nuclear", "Nuclear", False, "Non-renewable low-carbon"),
    ("UTE", "Thermal Other", "Thermal", False, "Thermal"),
]


def normalize_ascii(text: str) -> str:
    replacements = {
        "Á": "A", "À": "A", "Â": "A", "Ã": "A", "Ä": "A",
        "É": "E", "Ê": "E", "Í": "I", "Ó": "O", "Ô": "O", "Õ": "O",
        "Ú": "U", "Ç": "C", "á": "a", "à": "a", "â": "a", "ã": "a",
        "é": "e", "ê": "e", "í": "i", "ó": "o", "ô": "o", "õ": "o",
        "ú": "u", "ç": "c",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def classify_source(source: str, fuel: str = "") -> dict[str, object]:
    haystack = normalize_ascii(f"{source} {fuel}").upper()
    for token, grouped, tech, renewable, category in SOURCE_RULES:
        if token in haystack:
            return {
                "FonteAgrupada": grouped,
                "Tecnologia": tech,
                "Renovavel": renewable,
                "CategoriaPrincipal": category,
            }
    return {
        "FonteAgrupada": "Other",
        "Tecnologia": "Other",
        "Renovavel": False,
        "CategoriaPrincipal": "Other",
    }
