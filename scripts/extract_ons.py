from __future__ import annotations

import json

from src.common import ROOT, ckan_package, download, ensure_dirs, find_resource, read_config


def main() -> None:
    config = read_config()
    ensure_dirs(config)
    timeout = config["http"]["timeout_seconds"]
    retries = config["http"]["retries"]
    force = config["cache"]["force_download"]
    start = config["period"]["start_year"]
    end = config["period"]["end_year"]
    metadata = []

    balanco = config["sources"]["ons_balanco_subsistema"]
    package = ckan_package(balanco["ckan_api"], balanco["package_id"], timeout, retries)
    for year in range(start, end + 1):
        resource = find_resource(package, prefix=balanco["resource_prefix"], year=year)
        metadata.append(download(resource["url"], ROOT / f"data/raw/ons_balanco_{year}.csv", timeout, retries, force))
    print("[OK] ONS generation/load hourly balance")

    carga = config["sources"]["ons_carga_diaria"]
    package = ckan_package(carga["ckan_api"], carga["package_id"], timeout, retries)
    for year in range(start, end + 1):
        resource = find_resource(package, prefix=carga["resource_prefix"], year=year)
        metadata.append(download(resource["url"], ROOT / f"data/raw/ons_carga_diaria_{year}.csv", timeout, retries, force))
    print("[OK] ONS daily load")

    out = ROOT / "data/raw/metadata_ons.json"
    out.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
