export const config = {
  apiUrl: import.meta.env.VITE_API_URL || "",
  environment: import.meta.env.VITE_ENVIRONMENT || "development",
  supabaseUrl: import.meta.env.VITE_SUPABASE_URL || "",
  supabaseAnonKey: import.meta.env.VITE_SUPABASE_ANON_KEY || "",
  supabaseEnabled: Boolean(import.meta.env.VITE_SUPABASE_URL && import.meta.env.VITE_SUPABASE_ANON_KEY),
};

export const API_BASE = config.apiUrl || "";