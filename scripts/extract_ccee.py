from __future__ import annotations

import json

from src.common import ROOT, ckan_package, download, ensure_dirs, read_config


def main() -> None:
    config = read_config()
    ensure_dirs(config)
    timeout = config["http"]["timeout_seconds"]
    retries = config["http"]["retries"]
    force = config["cache"]["force_download"]
    source = config["sources"]["ccee_pld"]
    try:
        package = ckan_package(source["ckan_api"], source["package_id"], timeout, retries)
        start_year = int(config["period"]["start_year"])
        end_year = int(config["period"]["end_year"])
        resources = []
        for resource in package.get("resources", []):
            name = (resource.get("name") or "").lower()
            fmt = (resource.get("format") or "").lower()
            if "pld_media_mensal" not in name or "csv" not in fmt:
                continue
            if not any(str(year) in name for year in range(start_year, end_year + 1)):
                continue
            resources.append(resource)
        if not resources:
            raise RuntimeError("Nenhum recurso anual PLD_MEDIA_MENSAL encontrado no pacote CCEE.")
        metadata = []
        for resource in sorted(resources, key=lambda r: r.get("name") or ""):
            year = next((str(y) for y in range(start_year, end_year + 1) if str(y) in (resource.get("name") or "")), "periodo")
            destination = ROOT / f"data/raw/ccee_pld_media_mensal_{year}.csv"
            metadata.append(download(resource["url"], destination, timeout, retries, force))
        (ROOT / "data/raw/metadata_ccee.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        print("[OK] CCEE PLD")
    except Exception as exc:  # noqa: BLE001
        warning = {"source": "CCEE PLD", "status": "warning", "message": str(exc)}
        (ROOT / "data/raw/metadata_ccee.json").write_text(json.dumps([warning], ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[WARNING] CCEE indisponível: {exc}")


if __name__ == "__main__":
    main()
