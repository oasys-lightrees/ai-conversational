"use client";

import { type Locale, useI18n } from "@/lib/i18n";
import { cn } from "@/lib/utils";

const LOCALES: Locale[] = ["id", "en"];

/** ID / EN language switch. */
export function LanguageToggle() {
  const { locale, setLocale } = useI18n();
  return (
    <div className="inline-flex overflow-hidden rounded-lg border border-navy/20 text-xs">
      {LOCALES.map((code) => (
        <button
          key={code}
          type="button"
          onClick={() => setLocale(code)}
          aria-pressed={locale === code}
          className={cn(
            "px-2.5 py-1 font-semibold uppercase transition-colors",
            locale === code ? "bg-navy text-white" : "bg-white text-navy hover:bg-navy/5",
          )}
        >
          {code}
        </button>
      ))}
    </div>
  );
}
