"""Company list importer - parse CSV uploads or pasted text into companies."""

import csv
import io

COMPANY_COLUMNS = {
    "company",
    "company_name",
    "companyname",
    "name",
    "organization",
    "organisation",
    "account",
    "business",
}
DOMAIN_COLUMNS = {"domain", "website", "url", "web"}


def parse_csv(data: bytes | str) -> list[dict]:
    """Parse CSV/TSV content into rows of {company_name, domain}."""
    text = data.decode("utf-8-sig") if isinstance(data, bytes) else data
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";"])
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    if not reader.fieldnames:
        return []

    col_map: dict[str, str] = {}
    for field in reader.fieldnames:
        normalized = (field or "").strip().lower().replace(" ", "_")
        if normalized in COMPANY_COLUMNS:
            col_map.setdefault("company_name", field)
        elif normalized in DOMAIN_COLUMNS:
            col_map.setdefault("domain", field)

    rows: list[dict] = []
    for row in reader:
        name = (row.get(col_map.get("company_name") or "", "") or "").strip()
        if not name:
            continue
        rows.append(
            {
                "company_name": name,
                "domain": (row.get(col_map.get("domain") or "", "") or "").strip() or None,
            }
        )
    return rows


def parse_pasted_text(text: str) -> list[dict]:
    """Parse a newline/comma separated list of company names (and optional domains)."""
    rows: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        name = parts[0]
        if not name:
            continue
        rows.append({"company_name": name, "domain": parts[1] if len(parts) > 1 and parts[1] else None})
    return rows
