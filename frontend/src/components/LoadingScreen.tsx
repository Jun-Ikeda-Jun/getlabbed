"use client";

import type { Language } from "@/lib/types";

interface LoadingScreenProps {
  readonly step: number;
  readonly language: Language;
}

const STEPS_JA = [
  "動画をダウンロード中...",
  "フレームを分析中...",
  "AIがコーチング作成中...",
  "完了！結果を表示します",
];

const STEPS_EN = [
  "Downloading video...",
  "Analyzing frames...",
  "AI is writing your coaching...",
  "Done! Showing results",
];

const TIPS_JA = [
  "豆知識: ガーキャン上Bは多くのキャラの最速反撃手段です",
  "豆知識: 崖上がりは4択。毎回変えるだけで撃墜されにくくなります",
  "豆知識: シールドは時間で縮む。守りすぎもリスク",
  "豆知識: 着地狩りは「相手の真下」より「着地先を読む」が大事",
  "豆知識: 飛び道具は全部ガードする必要なし。小ジャンプで避けよう",
];

const TIPS_EN = [
  "Tip: Out-of-shield up B is the fastest punish for many characters",
  "Tip: Mix up your 4 ledge getup options to avoid getting punished",
  "Tip: Shield shrinks over time. Too much defense is also risky",
  "Tip: For landing traps, predict where they'll land, don't just chase",
  "Tip: You don't have to shield every projectile. Short hop over them",
];

export default function LoadingScreen({ step, language }: LoadingScreenProps) {
  const steps = language === "ja" ? STEPS_JA : STEPS_EN;
  const tips = language === "ja" ? TIPS_JA : TIPS_EN;
  const randomTip = tips[Math.floor(Math.random() * tips.length)];

  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center px-4">
      {/* Animated logo */}
      <div className="relative mb-8">
        <div className="w-20 h-20 rounded-2xl gradient-border p-0.5">
          <div className="w-full h-full rounded-2xl bg-[var(--color-bg-primary)] flex items-center justify-center">
            <span className="text-3xl">&#x1F3AE;</span>
          </div>
        </div>
        {/* Pulsing ring */}
        <div className="absolute inset-0 rounded-2xl border-2 border-[var(--color-accent-blue)] pulse-glow" />
      </div>

      {/* Steps */}
      <div className="w-full max-w-sm space-y-3 mb-8">
        {steps.map((label, i) => {
          const isActive = i === step;
          const isDone = i < step;

          return (
            <div key={label} className="flex items-center gap-3">
              {/* Step indicator */}
              <div
                className={`
                  w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold
                  transition-all duration-500
                  ${isDone ? "bg-[var(--color-accent-green)] text-black" : ""}
                  ${isActive ? "bg-[var(--color-accent-blue)] text-white glow-blue" : ""}
                  ${!isDone && !isActive ? "bg-[var(--color-border-subtle)] text-[var(--color-text-muted)]" : ""}
                `}
              >
                {isDone ? (
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  i + 1
                )}
              </div>

              {/* Label */}
              <span
                className={`
                  text-sm transition-colors duration-500
                  ${isDone ? "text-[var(--color-accent-green)]" : ""}
                  ${isActive ? "text-[var(--color-text-primary)] font-medium" : ""}
                  ${!isDone && !isActive ? "text-[var(--color-text-muted)]" : ""}
                `}
              >
                {label}
              </span>

              {/* Loading dots for active step */}
              {isActive && (
                <span className="flex gap-0.5 ml-1">
                  {[0, 1, 2].map((d) => (
                    <span
                      key={d}
                      className="w-1 h-1 rounded-full bg-[var(--color-accent-blue)]"
                      style={{
                        animation: `pulse-glow 1.4s ease-in-out ${d * 0.2}s infinite`,
                      }}
                    />
                  ))}
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Progress bar */}
      <div className="w-full max-w-sm h-1 bg-[var(--color-border-subtle)] rounded-full overflow-hidden mb-6">
        <div
          className="h-full bg-gradient-to-r from-[var(--color-accent-blue)] to-[var(--color-accent-purple)] rounded-full transition-all duration-1000 ease-out"
          style={{ width: `${((step + 1) / steps.length) * 100}%` }}
        />
      </div>

      {/* Random tip */}
      <div className="text-center max-w-md">
        <p className="text-xs text-[var(--color-text-muted)] leading-relaxed">
          &#x1F4A1; {randomTip}
        </p>
      </div>
    </div>
  );
}
