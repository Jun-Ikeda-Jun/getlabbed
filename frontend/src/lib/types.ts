export type MomentRating =
  | "great"
  | "good"
  | "okay"
  | "missed_opportunity"
  | "mistake"
  | "critical_error";

export interface MatchMoment {
  readonly timestamp: number;
  readonly description: string;
  readonly rating: MomentRating;
  readonly suggestion: string | null;
  readonly practice_tip: string | null;
}

export interface PlayerHabit {
  readonly habit: string;
  readonly description: string;
  readonly count: string;
  readonly impact: string;
  readonly fix: string;
}

export interface GameFlow {
  readonly game: number;
  readonly summary: string;
  readonly turning_point: string;
}

export interface MatchAnalysis {
  readonly summary: string;
  readonly score: number;
  readonly result: "win" | "loss" | "unknown";
  readonly stage: string;
  readonly player_character: string;
  readonly opponent_character: string;
  readonly habits: readonly PlayerHabit[];
  readonly moments: readonly MatchMoment[];
  readonly game_flow: readonly GameFlow[];
  readonly strengths: readonly string[];
  readonly weaknesses: readonly string[];
  readonly practice_plan: readonly string[];
  readonly matchup_tips: readonly string[];
  readonly pro_comparison: string;
}

export interface AnalyzeRequest {
  readonly youtube_url: string;
  readonly player_character: string;
  readonly opponent_character?: string;
  readonly mode?: "friendly" | "detailed";
  readonly language?: "ja" | "en";
}

export interface Character {
  readonly id: string;
  readonly name_en: string;
  readonly name_ja: string;
}

export interface Matchup {
  readonly char_a: string;
  readonly char_b: string;
  readonly tips: readonly string[];
  readonly advantage: "even" | "slight_advantage" | "advantage" | "disadvantage" | "slight_disadvantage";
}

export type AnalysisMode = "friendly" | "detailed";
export type Language = "ja" | "en";
