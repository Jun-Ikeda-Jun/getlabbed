import type { MomentRating } from "./types";

/**
 * Format seconds to MM:SS display
 */
export function formatTimestamp(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

/**
 * Get color classes for a moment rating
 */
export function getRatingColor(rating: MomentRating): string {
  const colors: Record<MomentRating, string> = {
    great: "text-emerald-400",
    good: "text-green-400",
    okay: "text-amber-400",
    missed_opportunity: "text-orange-400",
    mistake: "text-red-400",
    critical_error: "text-red-500",
  };
  return colors[rating];
}

export function getRatingBgColor(rating: MomentRating): string {
  const colors: Record<MomentRating, string> = {
    great: "bg-emerald-500/20 border-emerald-500/40",
    good: "bg-green-500/20 border-green-500/40",
    okay: "bg-amber-500/20 border-amber-500/40",
    missed_opportunity: "bg-orange-500/20 border-orange-500/40",
    mistake: "bg-red-500/20 border-red-500/40",
    critical_error: "bg-red-600/20 border-red-600/40",
  };
  return colors[rating];
}

export function getRatingDotColor(rating: MomentRating): string {
  const colors: Record<MomentRating, string> = {
    great: "bg-emerald-400",
    good: "bg-green-400",
    okay: "bg-amber-400",
    missed_opportunity: "bg-orange-400",
    mistake: "bg-red-400",
    critical_error: "bg-red-500",
  };
  return colors[rating];
}

export function getRatingIcon(rating: MomentRating): string {
  const icons: Record<MomentRating, string> = {
    great: "\u2705",
    good: "\u2714\uFE0F",
    okay: "\u27A1\uFE0F",
    missed_opportunity: "\u26A0\uFE0F",
    mistake: "\u274C",
    critical_error: "\uD83D\uDCA5",
  };
  return icons[rating];
}

export function getRatingLabel(rating: MomentRating, lang: "ja" | "en"): string {
  const labels: Record<MomentRating, { ja: string; en: string }> = {
    great: { ja: "ナイス！", en: "Great!" },
    good: { ja: "いいね", en: "Good" },
    okay: { ja: "まあまあ", en: "Okay" },
    missed_opportunity: { ja: "もったいない", en: "Missed" },
    mistake: { ja: "ミス", en: "Mistake" },
    critical_error: { ja: "要改善", en: "Critical" },
  };
  return labels[rating][lang];
}

/**
 * Get score color based on value 0-100
 */
export function getScoreColor(score: number): string {
  if (score >= 90) return "#3b82f6"; // blue
  if (score >= 70) return "#10b981"; // green
  if (score >= 50) return "#f59e0b"; // amber
  if (score >= 30) return "#f97316"; // orange
  return "#ef4444"; // red
}

/**
 * Validate YouTube URL
 */
export function isValidYouTubeUrl(url: string): boolean {
  const patterns = [
    /^https?:\/\/(www\.)?youtube\.com\/watch\?v=[\w-]+/,
    /^https?:\/\/youtu\.be\/[\w-]+/,
    /^https?:\/\/(www\.)?youtube\.com\/shorts\/[\w-]+/,
  ];
  return patterns.some((p) => p.test(url));
}
