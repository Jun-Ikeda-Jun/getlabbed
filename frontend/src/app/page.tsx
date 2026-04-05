"use client";

import { useState, useCallback } from "react";
import type { AnalysisMode, Language, MatchAnalysis } from "@/lib/types";
import { analyzeMatch } from "@/lib/api";
import { isValidYouTubeUrl } from "@/lib/utils";
import CharacterSelect from "@/components/CharacterSelect";
import LoadingScreen from "@/components/LoadingScreen";
import AnalysisResult from "@/components/AnalysisResult";

type AppState = "input" | "loading" | "result" | "error";

export default function Home() {
  const [state, setState] = useState<AppState>("input");
  const [language, setLanguage] = useState<Language>("ja");
  const [mode, setMode] = useState<AnalysisMode>("friendly");
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [playerCharacter, setPlayerCharacter] = useState("");
  const [opponentCharacter, setOpponentCharacter] = useState("");
  const [loadingStep, setLoadingStep] = useState(0);
  const [analysis, setAnalysis] = useState<MatchAnalysis | null>(null);
  const [error, setError] = useState("");

  const urlValid = youtubeUrl.trim() !== "" && isValidYouTubeUrl(youtubeUrl.trim());
  const canSubmit = urlValid && playerCharacter !== "";

  const handleSubmit = useCallback(async () => {
    if (!canSubmit) return;

    setState("loading");
    setLoadingStep(0);
    setError("");

    try {
      const result = await analyzeMatch(
        {
          youtube_url: youtubeUrl.trim(),
          player_character: playerCharacter,
          opponent_character: opponentCharacter || undefined,
          mode,
          language,
        },
        (step) => setLoadingStep(step),
      );
      setAnalysis(result);
      setState("result");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setError(message);
      setState("error");
    }
  }, [canSubmit, youtubeUrl, playerCharacter, opponentCharacter, mode, language]);

  const handleReset = useCallback(() => {
    setState("input");
    setAnalysis(null);
    setError("");
    setLoadingStep(0);
  }, []);

  // --- Loading state ---
  if (state === "loading") {
    return (
      <main className="min-h-screen">
        <Header language={language} onLanguageChange={setLanguage} />
        <LoadingScreen step={loadingStep} language={language} />
      </main>
    );
  }

  // --- Result state ---
  if (state === "result" && analysis) {
    return (
      <main className="min-h-screen">
        <Header language={language} onLanguageChange={setLanguage} />
        <AnalysisResult
          analysis={analysis}
          language={language}
          onReset={handleReset}
        />
      </main>
    );
  }

  // --- Input / Error state ---
  return (
    <main className="min-h-screen">
      <Header language={language} onLanguageChange={setLanguage} />

      {/* Hero Section */}
      <section className="pt-10 pb-6 px-4 text-center">
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-2">
          <span className="bg-gradient-to-r from-[var(--color-accent-orange)] via-[var(--color-accent-pink)] to-[var(--color-accent-amber)] bg-clip-text text-transparent">
            GetLabbed
          </span>
        </h1>
        <p className="text-lg md:text-2xl font-bold text-[var(--color-text-primary)] mb-2">
          {language === "ja"
            ? "お前の癖、丸見えだぞ？ 👀"
            : "Your habits are showing 👀"}
        </p>
        <p className="text-sm text-[var(--color-text-secondary)]">
          {language === "ja"
            ? "試合動画を貼るだけ。どこが強くてどこがヤバいか、全部教えてやるよ。"
            : "Paste your match. We'll show you what's fire and what's getting you punished."}
        </p>
      </section>

      {/* Main Input Area */}
      <section className="max-w-xl mx-auto px-4 pb-16">
        <div className="rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-card)] p-5 md:p-7 space-y-5">
          {/* YouTube URL */}
          <div>
            <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1.5">
              YouTube URL
            </label>
            <input
              type="url"
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              placeholder="https://youtube.com/watch?v=..."
              className={`
                w-full px-4 py-3 rounded-lg text-base
                bg-[var(--color-bg-secondary)] border
                placeholder:text-[var(--color-text-muted)]
                text-[var(--color-text-primary)]
                outline-none transition-all
                ${
                  youtubeUrl && !urlValid
                    ? "border-[var(--color-accent-red)] focus:border-[var(--color-accent-red)]"
                    : "border-[var(--color-border-accent)] focus:border-[var(--color-accent-blue)] focus:glow-blue"
                }
              `}
              onKeyDown={(e) => {
                if (e.key === "Enter" && canSubmit) handleSubmit();
              }}
            />
            {youtubeUrl && !urlValid && (
              <p className="mt-1 text-xs text-[var(--color-accent-red)]">
                {language === "ja"
                  ? "YouTubeのURLを入力してください"
                  : "Please enter a valid YouTube URL"}
              </p>
            )}
          </div>

          {/* Character selectors */}
          <CharacterSelect
            value={playerCharacter}
            onChange={setPlayerCharacter}
            label={language === "ja" ? "自分のキャラ" : "Your Character"}
            placeholder={language === "ja" ? "キャラ名で検索..." : "Search character..."}
          />

          <CharacterSelect
            value={opponentCharacter}
            onChange={setOpponentCharacter}
            label={language === "ja" ? "相手のキャラ（わかれば）" : "Opponent (optional)"}
            placeholder={language === "ja" ? "キャラ名で検索..." : "Search character..."}
            optional
          />

          {/* Mode toggle */}
          <div>
            <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
              {language === "ja" ? "レビューの深さ" : "Review depth"}
            </label>
            <div className="flex rounded-xl border border-[var(--color-border-accent)] overflow-hidden">
              <button
                onClick={() => setMode("friendly")}
                className={`
                  flex-1 py-2 text-sm font-medium transition-all
                  ${
                    mode === "friendly"
                      ? "bg-[var(--color-accent-green)]/20 text-[var(--color-accent-green)] border-r border-[var(--color-accent-green)]/30"
                      : "bg-transparent text-[var(--color-text-muted)] border-r border-[var(--color-border-accent)] hover:text-[var(--color-text-secondary)]"
                  }
                `}
              >
                {language === "ja" ? "🌱 わかりやすく" : "🌱 Easy"}
              </button>
              <button
                onClick={() => setMode("detailed")}
                className={`
                  flex-1 py-2 text-sm font-medium transition-all
                  ${
                    mode === "detailed"
                      ? "bg-[var(--color-accent-orange)]/20 text-[var(--color-accent-orange)]"
                      : "bg-transparent text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]"
                  }
                `}
              >
                {language === "ja" ? "⚔️ ガチ勢向け" : "⚔️ Pro"}
              </button>
            </div>
          </div>

          {/* Error message */}
          {state === "error" && (
            <div className="rounded-lg bg-[var(--color-accent-red)]/10 border border-[var(--color-accent-red)]/30 p-3">
              <p className="text-sm text-[var(--color-accent-red)]">
                {language === "ja"
                  ? `エラーが発生しました: ${error}`
                  : `An error occurred: ${error}`}
              </p>
            </div>
          )}

          {/* Submit button */}
          <button
            onClick={handleSubmit}
            disabled={!canSubmit}
            className={`
              w-full py-3.5 rounded-xl text-base font-bold
              transition-all btn-press
              ${
                canSubmit
                  ? "gradient-border text-white glow-blue hover:scale-[1.02]"
                  : "bg-[var(--color-border-subtle)] text-[var(--color-text-muted)] cursor-not-allowed"
              }
            `}
          >
            {language === "ja" ? "🔥 レビューしてもらう" : "🔥 Review My Match"}
          </button>
        </div>

        {/* Feature bullets */}
        <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-4">
          <FeatureCard
            icon="🎮"
            title={language === "ja" ? "動画を貼るだけ" : "Just Paste a Link"}
            description={
              language === "ja"
                ? "YouTubeのURLを貼れば、あとは全部やる"
                : "Drop a YouTube link and we handle the rest"
            }
          />
          <FeatureCard
            icon="💡"
            title={language === "ja" ? "ナイスとミス、全部わかる" : "Every Good & Bad Play"}
            description={
              language === "ja"
                ? "「ここナイス！」「ここもったいない！」を場面ごとに"
                : "Frame-by-frame breakdown of what worked and what didn't"
            }
          />
          <FeatureCard
            icon="💪"
            title={language === "ja" ? "今日からできる練習" : "Practice Right Away"}
            description={
              language === "ja"
                ? "トレモでそのまま試せる練習メニュー付き"
                : "Comes with drills you can try in training mode today"
            }
          />
        </div>
      </section>
    </main>
  );
}

// --- Sub-components ---

function Header({
  language,
  onLanguageChange,
}: {
  readonly language: Language;
  readonly onLanguageChange: (lang: Language) => void;
}) {
  return (
    <header className="flex items-center justify-between px-4 md:px-6 py-3 border-b border-[var(--color-border-subtle)]">
      <div className="flex items-center gap-2">
        <span className="text-xl">🔥</span>
        <span className="font-bold text-sm bg-gradient-to-r from-[var(--color-accent-orange)] to-[var(--color-accent-pink)] bg-clip-text text-transparent">
          GetLabbed
        </span>
      </div>

      {/* Language toggle */}
      <button
        onClick={() => onLanguageChange(language === "ja" ? "en" : "ja")}
        className="
          text-xs font-medium px-3 py-1.5 rounded-md
          border border-[var(--color-border-accent)]
          text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]
          hover:border-[var(--color-text-muted)]
          transition-all
        "
      >
        {language === "ja" ? "EN" : "JA"}
      </button>
    </header>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  readonly icon: string;
  readonly title: string;
  readonly description: string;
}) {
  return (
    <div className="rounded-2xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-card)] p-5 text-center hover:border-[var(--color-accent-orange)]/30 transition-all">
      <div className="text-3xl mb-2">{icon}</div>
      <h3 className="text-sm font-bold text-[var(--color-text-primary)] mb-1">
        {title}
      </h3>
      <p className="text-xs text-[var(--color-text-muted)] leading-relaxed">
        {description}
      </p>
    </div>
  );
}
