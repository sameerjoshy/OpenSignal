"""Company list importer - parse CSV uploads or pasted text into companies."""

import csv
import io
import re

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")


def extract_emails(text: str) -> list[str]:
    """Pull out and normalize email addresses from arbitrary text."""
    seen: dict[str, None] = {}
    for match in EMAIL_RE.finditer(text or ""):
        email = match.group(0).strip().lower()
        if email not in seen:
            seen[email] = None
    return list(seen)


def parse_email_file(data: bytes, filename: str = "") -> list[str]:
    """Parse a text/csv/xls/xlsx file into a list of unique emails."""
    name = (filename or "").lower()
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return _extract_from_spreadsheet(data, filename)
    text = data.decode("utf-8-sig", errors="replace")
    return extract_emails(text)


def _extract_from_spreadsheet(data: bytes, filename: str) -> list[str]:
    if filename.lower().endswith(".xlsx"):
        from openpyxl import load_workbook

        wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    else:
        import xlrd

        wb = xlrd.open_workbook(file_contents=data)

    emails: list[str] = []
    if filename.lower().endswith(".xlsx"):
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                for cell in row:
                    if isinstance(cell, str) and "@" in cell:
                        emails.extend(extract_emails(cell))
    else:
        for sheet in wb.sheets():
            for r in range(sheet.nrows):
                for c in range(sheet.ncols):
                    cell = sheet.cell_value(r, c)
                    if isinstance(cell, str) and "@" in cell:
                        emails.extend(extract_emails(cell))
    seen: dict[str, None] = {}
    result: list[str] = []
    for email in emails:
        if email not in seen:
            seen[email] = None
            result.append(email)
    return result

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
