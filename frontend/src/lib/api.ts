import type { AnalyzeRequest, Character, MatchAnalysis, Matchup } from "./types";
import { MOCK_ANALYSIS, MOCK_ANALYSIS_EN } from "./mock-data";
import { CHARACTERS } from "./characters";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const MOCK_MODE = process.env.NEXT_PUBLIC_MOCK_MODE === "true";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const errorBody = await res.text().catch(() => "Unknown error");
    throw new Error(`API error ${res.status}: ${errorBody}`);
  }

  return res.json() as Promise<T>;
}

function simulateDelay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function analyzeMatch(
  params: AnalyzeRequest,
  onProgress?: (step: number) => void,
): Promise<MatchAnalysis> {
  if (MOCK_MODE) {
    // Simulate the multi-step loading process
    onProgress?.(0);
    await simulateDelay(2000);
    onProgress?.(1);
    await simulateDelay(3000);
    onProgress?.(2);
    await simulateDelay(2000);
    onProgress?.(3);

    return params.language === "en" ? MOCK_ANALYSIS_EN : MOCK_ANALYSIS;
  }

  const data = await fetchApi<MatchAnalysis>("/api/analyze", {
    method: "POST",
    body: JSON.stringify(params),
  });

  return data;
}

export async function getCharacters(): Promise<readonly Character[]> {
  if (MOCK_MODE) {
    await simulateDelay(100);
    return CHARACTERS;
  }

  return fetchApi<Character[]>("/api/characters");
}

export async function getMatchup(charA: string, charB: string): Promise<Matchup> {
  if (MOCK_MODE) {
    await simulateDelay(300);
    return {
      char_a: charA,
      char_b: charB,
      tips: [
        "This is a mock matchup tip",
        "Another mock tip for this matchup",
      ],
      advantage: "even",
    };
  }

  return fetchApi<Matchup>(`/api/matchup/${charA}/${charB}`);
}

export async function healthCheck(): Promise<boolean> {
  if (MOCK_MODE) return true;

  try {
    await fetchApi("/api/health");
    return true;
  } catch {
    return false;
  }
}
