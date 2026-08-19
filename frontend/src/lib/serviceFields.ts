export interface ServiceField {
  key: string;
  label: string;
  placeholder: string;
  secret?: boolean;
  multiline?: boolean;
  target: "api_key" | string;
}

export const SERVICE_FIELDS: Record<string, ServiceField[]> = {
  apollo: [{ key: "api_key", label: "Apollo API key", placeholder: "apollo-…", secret: true, target: "api_key" }],
  hunter: [{ key: "api_key", label: "Hunter API key", placeholder: "hunter-…", secret: true, target: "api_key" }],
  newsapi: [{ key: "api_key", label: "NewsAPI key", placeholder: "…", secret: true, target: "api_key" }],
  mailgun: [
    { key: "api_key", label: "Mailgun API key", placeholder: "key-…", secret: true, target: "api_key" },
    { key: "domain", label: "Sending domain", placeholder: "mg.example.com", target: "config.domain" },
  ],
  sendgrid: [{ key: "api_key", label: "SendGrid API key", placeholder: "SG.…", secret: true, target: "api_key" }],
  hubspot: [{ key: "api_key", label: "HubSpot private app token", placeholder: "pat-…", secret: true, target: "api_key" }],
  salesforce: [
    { key: "client_id", label: "Client ID", placeholder: "…", target: "api_key" },
    { key: "client_secret", label: "Client secret", placeholder: "…", secret: true, target: "config.client_secret" },
    { key: "username", label: "Username", placeholder: "you@company.com", target: "config.username" },
    { key: "password", label: "Password", placeholder: "…", secret: true, target: "config.password" },
  ],
  ga4: [
    {
      key: "service_account_json",
      label: "Service account JSON",
      placeholder: '{ "type": "service_account", … }',
      multiline: true,
      target: "config.service_account_json",
    },
    { key: "property_id", label: "GA4 property ID", placeholder: "123456789", target: "config.property_id" },
  ],
  sec_edgar: [],
  deepseek: [],
};

export function serviceFields(service: string): ServiceField[] {
  return SERVICE_FIELDS[service] || [];
}

export function hasRequiredInput(service: string, values: Record<string, string>): boolean {
  const fields = serviceFields(service);
  if (fields.length === 0) return true;
  return fields.some((field) => Boolean((values[field.key] ?? "").trim()));
}