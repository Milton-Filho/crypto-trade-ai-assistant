import { DailyAnalysis, Settings } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getTodayAnalysis(): Promise<DailyAnalysis | null> {
  try {
    const res = await fetch(`${API_URL}/analysis/today`, { cache: 'no-store' });
    if (!res.ok) {
      if (res.status === 404) return null;
      throw new Error("Failed to fetch today's analysis");
    }
    return res.json();
  } catch (error) {
    console.error(error);
    return null;
  }
}

export async function getHistory(days: number = 30): Promise<DailyAnalysis[]> {
  try {
    const res = await fetch(`${API_URL}/analysis/history?days=${days}`, { cache: 'no-store' });
    if (!res.ok) throw new Error("Failed to fetch history");
    return res.json();
  } catch (error) {
    console.error(error);
    return [];
  }
}

export async function updateOutcome(id: string, outcome: string, price: number, note: string) {
  const res = await fetch(`${API_URL}/analysis/${id}/outcome`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ outcome, price, note })
  });
  if (!res.ok) throw new Error("Failed to update outcome");
  return res.json();
}

export async function getSettings(): Promise<Settings | null> {
  try {
    const res = await fetch(`${API_URL}/settings`, { cache: 'no-store' });
    if (!res.ok) throw new Error("Failed to fetch settings");
    return res.json();
  } catch (error) {
    console.error(error);
    return null;
  }
}

export async function updateSettings(settings: Partial<Settings>) {
  const res = await fetch(`${API_URL}/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings)
  });
  if (!res.ok) throw new Error("Failed to update settings");
  return res.json();
}
