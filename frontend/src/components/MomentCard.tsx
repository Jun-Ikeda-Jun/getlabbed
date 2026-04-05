"use client";

import { useState } from "react";
import type { MatchMoment } from "@/lib/types";
import type { Language } from "@/lib/types";
import {
  formatTimestamp,
  getRatingColor,
  getRatingBgColor,
  getRatingIcon,
  getRatingLabel,
} from "@/lib/utils";

interface MomentCardProps {
  readonly moment: MatchMoment;
  readonly language: Language;
}

export default function MomentCard({ moment, language }: MomentCardProps) {
  const [showTip, setShowTip] = useState(false);

  return (
    <div
      className={`
        rounded-xl border p-4 transition-all duration-300
        ${getRatingBgColor(moment.rating)}
      `}
    >
      {/* Header */}
      <div className="flex items-start gap-3 mb-2">
        <span className="text-lg">{getRatingIcon(moment.rating)}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-mono text-[var(--color-text-muted)] bg-black/30 px-2 py-0.5 rounded">
              {formatTimestamp(moment.timestamp)}
            </span>
            <span className={`text-sm font-bold ${getRatingColor(moment.rating)}`}>
              {getRatingLabel(moment.rating, language)}
            </span>
          </div>
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-[var(--color-text-primary)] leading-relaxed mb-3 ml-8">
        {moment.description}
      </p>

      {/* Suggestion */}
      {moment.suggestion && (
        <div className="ml-8 mb-3 pl-3 border-l-2 border-[var(--color-accent-blue)]/40">
          <p className="text-sm text-[var(--color-accent-blue)]">
            {moment.suggestion}
          </p>
        </div>
      )}

      {/* Practice Tip (collapsible) */}
      {moment.practice_tip && (
        <div className="ml-8">
          <button
            onClick={() => setShowTip((prev) => !prev)}
            className="text-xs font-medium text-[var(--color-accent-purple)] hover:text-[var(--color-accent-purple)]/80 transition-colors flex items-center gap-1"
          >
            <svg
              className={`w-3 h-3 transition-transform ${showTip ? "rotate-90" : ""}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            {language === "ja" ? "練習メニュー" : "Practice Tip"}
          </button>

          {showTip && (
            <p className="mt-2 text-xs text-[var(--color-text-secondary)] bg-black/20 rounded-lg p-3 leading-relaxed">
              {moment.practice_tip}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
