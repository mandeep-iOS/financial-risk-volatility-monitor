import type { CompareResponse, EvidenceResponse, ForecastResponse, HealthResponse, OverviewResponse, SymbolInfo } from './types'

const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, init)
  if (!response.ok) {
    throw new Error(`API request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

export const api = {
  health: () => request<HealthResponse>('/health'),
  symbols: () => request<SymbolInfo[]>('/symbols'),
  forecast: (symbol: string, horizon = 5) =>
    request<ForecastResponse>('/forecast', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol, horizon }),
    }),
  overview: (symbol: string, portfolioValue = 10000) =>
    request<OverviewResponse>(`/overview/${symbol}?portfolio_value=${portfolioValue}`),
  compare: (startDate?: string, endDate?: string) => request<CompareResponse>(`/compare${startDate ? `?start_date=${startDate}&end_date=${endDate}` : ''}`),
  evidence: () => request<EvidenceResponse>('/evidence'),
}
