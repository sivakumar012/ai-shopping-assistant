import { API_BASE, API_KEY } from "../constants/config";

const headers = {
  "Content-Type": "application/json",
  "X-API-Key": API_KEY,
};

export type Alert = {
  id: number;
  product_name: string;
  product_url: string;
  target_price: number;
  current_price: number | null;
  whatsapp_number: string | null;
  webhook_url: string | null;
  is_active: boolean;
  notified: boolean;
  created_at: string;
};

export type CreateAlertPayload = {
  product_name: string;
  product_url: string;
  target_price: number;
  whatsapp_number?: string;
  webhook_url?: string;
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  listAlerts: () => request<Alert[]>("/v1/alerts"),

  createAlert: (payload: CreateAlertPayload) =>
    request<Alert>("/v1/alerts", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  deleteAlert: (id: number) =>
    request<{ detail: string }>(`/v1/alerts/${id}`, { method: "DELETE" }),

  resetAlert: (id: number) =>
    request<Alert>(`/v1/alerts/${id}/reset`, { method: "POST" }),

  updateAlert: (id: number, patch: Partial<Alert>) =>
    request<Alert>(`/v1/alerts/${id}`, {
      method: "PATCH",
      body: JSON.stringify(patch),
    }),

  triggerCheck: () =>
    request<{ detail: string }>("/v1/check", { method: "POST" }),
};
