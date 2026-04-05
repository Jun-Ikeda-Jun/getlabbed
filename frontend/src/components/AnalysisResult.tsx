"use client";

import { useState } from "react";
import type { MatchAnalysis, Language } from "@/lib/types";
import { CHARACTERS } from "@/lib/characters";
import ScoreCircle from "./ScoreCircle";
import MomentTimeline from "./MomentTimeline";
import MomentCard from "./MomentCard";
import AnalysisSection from "./AnalysisSection";

interface AnalysisResultProps {
  readonly analysis: MatchAnalysis;
  readonly language: Language;
  readonly onReset: () => void;
}

function getCharacterName(id: string, lang: Language): string {
  const char = CHARACTERS.find((c) => c.id === id);
  if (!char) return id;
  return lang === "ja" ? char.name_ja : char.name_en;
}

export default function AnalysisResult({
  analysis,
  language,
  onReset,
}: AnalysisResultProps) {
  const [selectedMomentIndex, setSelectedMomentIndex] = useState<number | null>(null);

  const selectedMoment =
    selectedMomentIndex !== null ? analysis.moments[selectedMomentIndex] : null;

  const playerName = getCharacterName(analysis.player_character, language);
  const opponentName = getCharacterName(analysis.opponent_character, language);

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      {/* Back button */}
      <button
        onClick={onReset}
        className="flex items-center gap-1.5 text-sm text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] transition-colors"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        {language === "ja" ? "新しい試合を分析" : "Analyze another match"}
      </button>

      {/* Match Summary Card */}
      <div className="rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-card)] p-5 md:p-6">
        <div className="flex flex-col md:flex-row items-center gap-5">
          {/* Score */}
          <ScoreCircle score={analysis.score} size={100} />

          {/* Info */}
          <div className="flex-1 text-center md:text-left">
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-3 mb-2">
              {/* Result badge */}
              <span
                className={`
                  text-xs font-bold px-2.5 py-1 rounded-full uppercase tracking-wide
                  ${analysis.result === "win" ? "bg-[var(--color-accent-green)]/20 text-[var(--color-accent-green)]" : ""}
                  ${analysis.result === "loss" ? "bg-[var(--color-accent-red)]/20 text-[var(--color-accent-red)]" : ""}
                  ${analysis.result === "unknown" ? "bg-[var(--color-border-accent)] text-[var(--color-text-muted)]" : ""}
                `}
              >
                {analysis.result === "win" && (language === "ja" ? "WIN" : "WIN")}
                {analysis.result === "loss" && (language === "ja" ? "LOSE" : "LOSS")}
                {analysis.result === "unknown" && "---"}
              </span>

              {/* Characters */}
              <span className="text-sm text-[var(--color-text-secondary)]">
                {playerName} vs {opponentName}
              </span>

              {/* Stage */}
              <span className="text-xs text-[var(--color-text-muted)] bg-[var(--color-bg-secondary)] px-2 py-0.5 rounded">
                {analysis.stage}
              </span>
            </div>

            <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
              {analysis.summary}
            </p>
          </div>
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <AnalysisSection
          title={language === "ja" ? "良かった点" : "Strengths"}
          icon={<span>&#x1F4AA;</span>}
        >
          <ul className="space-y-2">
            {analysis.strengths.map((s) => (
              <li key={s} className="flex items-start gap-2 text-sm">
                <span className="text-[var(--color-accent-green)] mt-0.5 shrink-0">&#x2714;</span>
                <span className="text-[var(--color-text-secondary)]">{s}</span>
              </li>
            ))}
          </ul>
        </AnalysisSection>

        <AnalysisSection
          title={language === "ja" ? "改善ポイント" : "Areas to Improve"}
          icon={<span>&#x1F3AF;</span>}
        >
          <ul className="space-y-2">
            {analysis.weaknesses.map((w) => (
              <li key={w} className="flex items-start gap-2 text-sm">
                <span className="text-[var(--color-accent-red)] mt-0.5 shrink-0">&#x2716;</span>
                <span className="text-[var(--color-text-secondary)]">{w}</span>
              </li>
            ))}
          </ul>
        </AnalysisSection>
      </div>

      {/* Key Moments */}
      <AnalysisSection
        title={language === "ja" ? "試合のキーモーメント" : "Key Moments"}
        icon={<span>&#x23F1;&#xFE0F;</span>}
      >
        {/* Timeline */}
        <MomentTimeline
          moments={analysis.moments}
          selectedIndex={selectedMomentIndex}
          onSelect={setSelectedMomentIndex}
        />

        {/* Selected moment detail */}
        {selectedMoment ? (
          <div className="mt-4">
            <MomentCard moment={selectedMoment} language={language} />
          </div>
        ) : (
          <p className="mt-4 text-center text-sm text-[var(--color-text-muted)]">
            {language === "ja"
              ? "タイムライン上のポイントをクリックして詳細を表示"
              : "Click a point on the timeline to see details"}
          </p>
        )}

        {/* All moments list */}
        <div className="mt-6 space-y-3">
          <h3 className="text-sm font-medium text-[var(--color-text-muted)]">
            {language === "ja" ? "全モーメント" : "All Moments"}
          </h3>
          {analysis.moments.map((moment, index) => (
            <div
              key={`${moment.timestamp}-${index}`}
              className={`cursor-pointer transition-opacity ${
                selectedMomentIndex === index ? "opacity-100" : "opacity-70 hover:opacity-100"
              }`}
              onClick={() => setSelectedMomentIndex(index)}
            >
              <MomentCard moment={moment} language={language} />
            </div>
          ))}
        </div>
      </AnalysisSection>

      {/* Practice Plan */}
      <AnalysisSection
        title={language === "ja" ? "練習メニュー" : "Practice Plan"}
        icon={<span>&#x1F4DD;</span>}
      >
        <ol className="space-y-3">
          {analysis.practice_plan.map((item, index) => (
            <li key={item} className="flex items-start gap-3 text-sm">
              <span className="shrink-0 w-6 h-6 rounded-full bg-[var(--color-accent-purple)]/20 text-[var(--color-accent-purple)] flex items-center justify-center text-xs font-bold">
                {index + 1}
              </span>
              <span className="text-[var(--color-text-secondary)] leading-relaxed">
                {item}
              </span>
            </li>
          ))}
        </ol>
      </AnalysisSection>

      {/* Matchup Tips */}
      {analysis.matchup_tips.length > 0 && (
        <AnalysisSection
          title={
            language === "ja"
              ? `${playerName} vs ${opponentName} のポイント`
              : `${playerName} vs ${opponentName} Tips`
          }
          icon={<span>&#x2694;&#xFE0F;</span>}
        >
          <ul className="space-y-2">
            {analysis.matchup_tips.map((tip) => (
              <li key={tip} className="flex items-start gap-2 text-sm">
                <span className="text-[var(--color-accent-cyan)] mt-0.5 shrink-0">&#x25B8;</span>
                <span className="text-[var(--color-text-secondary)]">{tip}</span>
              </li>
            ))}
          </ul>
        </AnalysisSection>
      )}

      {/* Analyze another */}
      <div className="text-center pt-4">
        <button
          onClick={onReset}
          className="
            px-6 py-3 rounded-lg
            bg-[var(--color-bg-card)] border border-[var(--color-border-accent)]
            text-[var(--color-text-secondary)] text-sm font-medium
            hover:border-[var(--color-accent-blue)] hover:text-[var(--color-accent-blue)]
            transition-all btn-press
          "
        >
          {language === "ja" ? "別の試合を分析する" : "Analyze Another Match"}
        </button>
      </div>
    </div>
  );
}
