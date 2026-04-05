"use client";

import type { MatchMoment } from "@/lib/types";
import { formatTimestamp, getRatingDotColor } from "@/lib/utils";

interface MomentTimelineProps {
  readonly moments: readonly MatchMoment[];
  readonly selectedIndex: number | null;
  readonly onSelect: (index: number) => void;
}

export default function MomentTimeline({
  moments,
  selectedIndex,
  onSelect,
}: MomentTimelineProps) {
  if (moments.length === 0) return null;

  const maxTimestamp = Math.max(...moments.map((m) => m.timestamp));

  return (
    <div className="w-full">
      {/* Timeline track */}
      <div className="relative h-12 flex items-center">
        {/* Background line */}
        <div className="absolute left-0 right-0 h-0.5 bg-[var(--color-border-accent)] rounded-full" />

        {/* Dots */}
        {moments.map((moment, index) => {
          const position = maxTimestamp > 0 ? (moment.timestamp / maxTimestamp) * 100 : 0;
          const isSelected = selectedIndex === index;

          return (
            <button
              key={`${moment.timestamp}-${index}`}
              className={`
                timeline-dot absolute z-10
                rounded-full border-2 border-[var(--color-bg-primary)]
                ${getRatingDotColor(moment.rating)}
                ${isSelected ? "w-5 h-5 -ml-2.5 ring-2 ring-white/30" : "w-3.5 h-3.5 -ml-1.5"}
              `}
              style={{ left: `${Math.max(2, Math.min(98, position))}%` }}
              onClick={() => onSelect(index)}
              aria-label={`Moment at ${formatTimestamp(moment.timestamp)}`}
            >
              {/* Tooltip on hover */}
              <span className="absolute -top-7 left-1/2 -translate-x-1/2 text-xs text-[var(--color-text-muted)] whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none">
                {formatTimestamp(moment.timestamp)}
              </span>
            </button>
          );
        })}
      </div>

      {/* Timestamps at edges */}
      <div className="flex justify-between text-xs text-[var(--color-text-muted)] mt-1 px-1">
        <span>0:00</span>
        <span>{formatTimestamp(maxTimestamp)}</span>
      </div>
    </div>
  );
}
