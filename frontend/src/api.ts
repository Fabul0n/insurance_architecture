export type User = {
  id: number;
  full_name: string;
  passport_data: string;
  birth_date: string;
  email: string;
};

export type AppContract = {
  id: number;
  contract_number: string;
  application_id: number;
  created_at: string;
};

export type Application = {
  id: number;
  status: string;
  full_name: string;
  passport_data: string;
  birth_date: string;
  email: string;
  workplace: string;
  insurance_object: string;
  insurance_period_months: number;
  insurance_cases: string[];
  payout_amount: string;
  created_at: string;
};

export type LastApplication = Application | null;
export type PersonalDataPolicy = {
  title: string;
  updated_at: string;
  sections: string[];
};

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api/insurance";

type RequestOptions = {
  method?: string;
  body?: unknown;
  token?: string | null;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method ?? "GET",
    headers: {
      "Content-Type": "application/json",
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {})
    },
    body: options.body ? JSON.stringify(options.body) : undefined
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({ detail: "Ошибка запроса" }));
    throw new Error(data.detail ?? "Ошибка запроса");
  }

  return response.json() as Promise<T>;
}

export const api = {
  getContent: () =>
    request<{ title: string; paragraphs: string[]; note_for_guests: string }>("/content"),
  getPolicy: () => request<PersonalDataPolicy>("/policy"),

  register: (payload: {
    full_name: string;
    passport_data: string;
    birth_date: string;
    email: string;
    password: string;
    pdn_consent: true;
  }) => request<{ access_token: string }>("/auth/register", { method: "POST", body: payload }),

  login: (payload: { email: string; password: string }) =>
    request<{ access_token: string }>("/auth/login", { method: "POST", body: payload }),

  me: (token: string) => request<User>("/me", { token }),

  createApplication: (
    token: string,
    payload: {
      full_name: string;
      passport_data: string;
      birth_date: string;
      email: string;
      workplace: string;
      insurance_object: string;
      insurance_period_months: number;
      insurance_cases: string[];
      payout_amount: number;
      pdn_consent: true;
    }
  ) => request<Application>("/applications", { method: "POST", token, body: payload }),

  getLastApplication: (token: string) => request<LastApplication>("/applications/last", { token }),
  getApplications: (token: string) => request<Application[]>("/applications", { token }),

  pay: (
    token: string,
    payload: {
      application_id: number;
      payment_method: "sbp" | "card";
      card_number?: string;
      card_holder?: string;
      card_expiry?: string;
      card_cvc?: string;
    }
  ) => request<{ status: "failed" | "success"; message: string }>("/payments", { method: "POST", token, body: payload }),

  contracts: (token: string) => request<AppContract[]>("/contracts", { token }),

  contractDownloadUrl: (id: number, format: "pdf" | "docx", token: string) =>
    `${API_BASE}/contracts/${id}/download?format=${format}&token=${encodeURIComponent(token)}`
};
