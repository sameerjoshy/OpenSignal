import { createClient, SupabaseClient } from "@supabase/supabase-js";
import { config } from "../config";

let client: SupabaseClient | null = null;

if (config.supabaseEnabled) {
  client = createClient(config.supabaseUrl, config.supabaseAnonKey);
}

export const supabase = client;

export function isSupabaseEnabled(): boolean {
  return supabase !== null;
}