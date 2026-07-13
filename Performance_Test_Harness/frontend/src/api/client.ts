import type {
  ConfigResponse,
  StartTestResponse,
  TestConfigRequest,
  TestStatusResponse,
} from "./types";

const STORAGE_KEY = "rdp_harness_api_base_url";

const DEFAULT_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://localhost:8000";

export function getApiBaseUrl(): string {
  return localStorage.getItem(STORAGE_KEY) ?? DEFAULT_BASE_URL;
}

export function setApiBaseUrl(url: string): void {
  localStorage.setItem(STORAGE_KEY, url.replace(/\/+$/, ""));
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${getApiBaseUrl()}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore non-JSON error bodies
    }
    throw new Error(`${res.status}: ${detail}`);
  }
  return (await res.json()) as T;
}

export function fetchConfig(): Promise<ConfigResponse> {
  return request<ConfigResponse>("/api/config");
}

export function checkHealth(): Promise<{ status: string }> {
  return request<{ status: string }>("/api/health");
}

export function startTest(cfg: TestConfigRequest): Promise<StartTestResponse> {
  return request<StartTestResponse>("/api/tests", {
    method: "POST",
    body: JSON.stringify(cfg),
  });
}

export function getTest(testId: string): Promise<TestStatusResponse> {
  return request<TestStatusResponse>(`/api/tests/${testId}`);
}

export function stopTest(testId: string): Promise<{ stopped: boolean }> {
  return request<{ stopped: boolean }>(`/api/tests/${testId}/stop`, {
    method: "POST",
  });
}
