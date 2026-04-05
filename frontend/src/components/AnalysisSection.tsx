import type { ReactNode } from "react";

interface AnalysisSectionProps {
  readonly title: string;
  readonly icon: ReactNode;
  readonly children: ReactNode;
  readonly className?: string;
}

export default function AnalysisSection({
  title,
  icon,
  children,
  className = "",
}: AnalysisSectionProps) {
  return (
    <section
      className={`
        rounded-xl border border-[var(--color-border-subtle)]
        bg-[var(--color-bg-card)] p-5 md:p-6
        ${className}
      `}
    >
      <div className="flex items-center gap-2.5 mb-4">
        <span className="text-xl">{icon}</span>
        <h2 className="text-lg font-bold text-[var(--color-text-primary)]">
          {title}
        </h2>
      </div>
      {children}
    </section>
  );
}
