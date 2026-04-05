"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import type { Character } from "@/lib/types";
import { CHARACTERS } from "@/lib/characters";

interface CharacterSelectProps {
  readonly value: string;
  readonly onChange: (characterId: string) => void;
  readonly label: string;
  readonly placeholder: string;
  readonly optional?: boolean;
}

export default function CharacterSelect({
  value,
  onChange,
  label,
  placeholder,
  optional = false,
}: CharacterSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const selectedChar = CHARACTERS.find((c) => c.id === value);

  const filtered = search
    ? CHARACTERS.filter(
        (c) =>
          c.name_en.toLowerCase().includes(search.toLowerCase()) ||
          c.name_ja.includes(search),
      )
    : CHARACTERS;

  const handleSelect = useCallback(
    (char: Character) => {
      onChange(char.id);
      setSearch("");
      setIsOpen(false);
    },
    [onChange],
  );

  const handleClear = useCallback(() => {
    onChange("");
    setSearch("");
  }, [onChange]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        setSearch("");
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div ref={containerRef} className="relative">
      <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-1.5">
        {label}
        {optional && (
          <span className="ml-1 text-xs text-[var(--color-text-muted)]">(optional)</span>
        )}
      </label>

      <div
        className={`
          flex items-center gap-2 px-3 py-2.5 rounded-lg border cursor-pointer
          transition-all duration-200
          ${
            isOpen
              ? "border-[var(--color-accent-blue)] bg-[var(--color-bg-secondary)] glow-blue"
              : "border-[var(--color-border-accent)] bg-[var(--color-bg-card)] hover:border-[var(--color-text-muted)]"
          }
        `}
        onClick={() => {
          setIsOpen(true);
          setTimeout(() => inputRef.current?.focus(), 0);
        }}
      >
        {isOpen ? (
          <input
            ref={inputRef}
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={placeholder}
            className="flex-1 bg-transparent outline-none text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)]"
            onKeyDown={(e) => {
              if (e.key === "Escape") {
                setIsOpen(false);
                setSearch("");
              }
              if (e.key === "Enter" && filtered.length === 1) {
                handleSelect(filtered[0]);
              }
            }}
          />
        ) : (
          <span
            className={`flex-1 ${selectedChar ? "text-[var(--color-text-primary)]" : "text-[var(--color-text-muted)]"}`}
          >
            {selectedChar
              ? `${selectedChar.name_ja} / ${selectedChar.name_en}`
              : placeholder}
          </span>
        )}

        {value && !isOpen && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleClear();
            }}
            className="text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] transition-colors"
            aria-label="Clear selection"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}

        <svg
          className={`w-4 h-4 text-[var(--color-text-muted)] transition-transform ${isOpen ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      {isOpen && (
        <div className="absolute z-50 mt-1 w-full max-h-60 overflow-y-auto rounded-lg border border-[var(--color-border-accent)] bg-[var(--color-bg-card)] shadow-xl">
          {filtered.length === 0 ? (
            <div className="px-3 py-4 text-center text-sm text-[var(--color-text-muted)]">
              No characters found
            </div>
          ) : (
            filtered.map((char) => (
              <button
                key={char.id}
                onClick={() => handleSelect(char)}
                className={`
                  w-full text-left px-3 py-2 text-sm transition-colors
                  hover:bg-[var(--color-bg-card-hover)]
                  ${char.id === value ? "bg-[var(--color-accent-blue)]/10 text-[var(--color-accent-blue)]" : "text-[var(--color-text-primary)]"}
                `}
              >
                <span className="font-medium">{char.name_ja}</span>
                <span className="ml-2 text-[var(--color-text-muted)]">{char.name_en}</span>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
