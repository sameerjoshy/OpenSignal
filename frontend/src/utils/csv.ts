/** Parse pasted company list / CSV text into rows of {company_name, domain}. */
export interface CompanyRow {
  company_name: string;
  domain?: string | null;
}

export function parseCompaniesText(text: string): CompanyRow[] {
  const rows: CompanyRow[] = [];
  for (const line of text.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    const parts = trimmed.split(",").map((p) => p.trim());
    if (!parts[0]) continue;
    rows.push({ company_name: parts[0], domain: parts[1] || null });
  }
  return rows;
}

export async function parseCompanyCsv(file: File): Promise<CompanyRow[]> {
  const text = await file.text();
  const lines = text.split(/\r?\n/);
  if (lines.length === 0) return [];
  const header = lines[0].toLowerCase();
  const hasHeader =
    header.includes("company") || header.includes("name") || header.includes("organization") || header.includes("account");

  const rows: CompanyRow[] = [];
  const start = hasHeader ? 1 : 0;
  for (let i = start; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    const parts = line.split(",").map((p) => p.trim().replace(/^"|"$/g, ""));
    if (!parts[0]) continue;
    rows.push({ company_name: parts[0], domain: parts[1] || null });
  }
  return rows;
}