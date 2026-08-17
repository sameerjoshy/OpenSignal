import { describe, expect, it } from "vitest";
import { parseCompaniesText, parseCompanyCsv } from "./csv";

describe("parseCompaniesText", () => {
  it("parses simple company names", () => {
    const rows = parseCompaniesText("Acme Inc.\nGlobex Corp\n");
    expect(rows).toEqual([
      { company_name: "Acme Inc.", domain: null },
      { company_name: "Globex Corp", domain: null },
    ]);
  });

  it("parses name,domain pairs", () => {
    const rows = parseCompaniesText("Acme Inc.,acme.com\nGlobex Corp, globex.io");
    expect(rows[0]).toEqual({ company_name: "Acme Inc.", domain: "acme.com" });
    expect(rows[1]).toEqual({ company_name: "Globex Corp", domain: "globex.io" });
  });

  it("ignores blank lines", () => {
    expect(parseCompaniesText("").length).toBe(0);
    expect(parseCompaniesText("\n  \nAcme\n").length).toBe(1);
  });
});

function makeCsvFile(content: string): File {
  const file = new File([content], "companies.csv");
  Object.defineProperty(file, "text", {
    value: () => Promise.resolve(content),
  });
  return file;
}

describe("parseCompanyCsv", () => {
  it("skips a header row when present", async () => {
    const rows = await parseCompanyCsv(makeCsvFile("company,domain\nAcme,acme.com\nGlobex,globex.io\n"));
    expect(rows).toEqual([
      { company_name: "Acme", domain: "acme.com" },
      { company_name: "Globex", domain: "globex.io" },
    ]);
  });

  it("handles CSV without header", async () => {
    const rows = await parseCompanyCsv(makeCsvFile("Acme,acme.com\nGlobex\n"));
    expect(rows).toEqual([
      { company_name: "Acme", domain: "acme.com" },
      { company_name: "Globex", domain: null },
    ]);
  });
});