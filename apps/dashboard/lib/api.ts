export function apiBase(): string {
  return process.env.NEXT_PUBLIC_SALES_API ?? "http://127.0.0.1:8000";
}

export async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, { ...init, cache: "no-store" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}
