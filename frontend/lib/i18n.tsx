"use client";

// Lightweight UI internationalization (English / Bahasa Indonesia).
//
// This translates the app *chrome* (labels, buttons, static copy, LIA's
// opening line, stage names). AI-generated content — LIA's chat replies and the
// report narrative/recommendations — comes from the backend in Bahasa
// Indonesia and is not translated here; that would require threading the locale
// through to the backend prompts.

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export type Locale = "id" | "en";

const STORAGE_KEY = "locale";
const DEFAULT_LOCALE: Locale = "id";

const dictionaries: Record<Locale, Record<string, string>> = {
  id: {
    "hero.title": "Asesmen Bisnis Properti berbasis AI",
    "hero.subtitle":
      "Nilai bisnis properti Anda melalui percakapan natural dan terima rekomendasi berbasis AI dari LIA.",
    "cta.start": "Mulai Asesmen",
    "cta.resume": "Lanjutkan Asesmen",
    "cta.new": "Mulai Baru",
    "feature.chat.title": "Percakapan Natural",
    "feature.chat.desc": "Jawab pertanyaan LIA seperti mengobrol biasa — tanpa formulir panjang.",
    "feature.analysis.title": "Analisis Terstruktur",
    "feature.analysis.desc": "Informasi bisnis Anda diekstrak dan dinilai secara otomatis.",
    "feature.reco.title": "Rekomendasi AI",
    "feature.reco.desc": "Terima laporan dan rekomendasi yang dipersonalisasi untuk properti Anda.",
    "chat.greeting":
      "Halo, saya LIA. Saya akan membantu menilai bisnis properti Anda melalui percakapan singkat. Untuk memulai, boleh ceritakan tentang properti Anda?",
    "chat.placeholder": "Ketik pesan Anda...",
    "chat.send": "Kirim pesan",
    "chat.typing": "LIA sedang mengetik...",
    "assessment.loading": "Memuat asesmen...",
    "stage.PROPERTY_PROFILE": "Profil Properti",
    "stage.BUSINESS_STAGE": "Tahap Bisnis",
    "stage.BRANCH": "Detail Bisnis",
    "stage.OPERATIONS": "Operasional",
    "stage.TECHNOLOGY": "Teknologi",
    "stage.PAIN_POINTS": "Tantangan",
    "stage.GOALS": "Tujuan",
    "stage.COMPLETE": "Selesai",
    "stage.default": "Asesmen",
    "report.title": "Laporan Asesmen",
    "report.download": "Unduh PDF",
    "report.startNew": "Mulai Asesmen Baru",
    "report.loading": "Memuat laporan...",
    "report.error": "Laporan tidak ditemukan.",
    "report.summary": "Ringkasan Eksekutif",
    "report.section.business": "Analisis Bisnis",
    "report.section.operational": "Analisis Operasional",
    "report.section.technology": "Analisis Teknologi",
    "report.section.aiReadiness": "Kesiapan AI",
    "report.section.recoSummary": "Ringkasan Rekomendasi",
    "report.section.nextSteps": "Langkah Berikutnya",
    "report.reco": "Rekomendasi",
    "report.impact": "Dampak",
    "priority.HIGH": "Prioritas Tinggi",
    "priority.MEDIUM": "Prioritas Sedang",
    "priority.LOW": "Prioritas Rendah",
    "property.title": "Profil Properti",
    "property.name": "Nama",
    "property.type": "Jenis",
    "property.location": "Lokasi",
    "property.stage": "Tahap Bisnis",
    "property.units": "Jumlah Unit",
    "loading.title": "Membuat Laporan",
    "loading.message": "LIA sedang menganalisis hasil asesmen Anda...",
    "loading.retry": "Coba lagi",
    "loading.notFound": "Asesmen tidak ditemukan.",
    "loading.error": "Gagal membuat laporan.",
    "error.generic": "Terjadi kesalahan. Silakan coba lagi.",
    "notfound.message": "Halaman tidak ditemukan.",
    "notfound.back": "Kembali ke beranda",
  },
  en: {
    "hero.title": "AI-Powered Property Business Assessment",
    "hero.subtitle":
      "Assess your property business through a natural conversation and receive AI-driven recommendations from LIA.",
    "cta.start": "Start Assessment",
    "cta.resume": "Resume Assessment",
    "cta.new": "Start New",
    "feature.chat.title": "Natural Conversation",
    "feature.chat.desc": "Answer LIA's questions like a normal chat — no long forms.",
    "feature.analysis.title": "Structured Analysis",
    "feature.analysis.desc": "Your business information is extracted and scored automatically.",
    "feature.reco.title": "AI Recommendations",
    "feature.reco.desc": "Receive a personalized report and recommendations for your property.",
    "chat.greeting":
      "Hi, I'm LIA. I'll help assess your property business through a short conversation. To start, could you tell me about your property?",
    "chat.placeholder": "Type your message...",
    "chat.send": "Send message",
    "chat.typing": "LIA is typing...",
    "assessment.loading": "Loading assessment...",
    "stage.PROPERTY_PROFILE": "Property Profile",
    "stage.BUSINESS_STAGE": "Business Stage",
    "stage.BRANCH": "Business Details",
    "stage.OPERATIONS": "Operations",
    "stage.TECHNOLOGY": "Technology",
    "stage.PAIN_POINTS": "Challenges",
    "stage.GOALS": "Goals",
    "stage.COMPLETE": "Done",
    "stage.default": "Assessment",
    "report.title": "Assessment Report",
    "report.download": "Download PDF",
    "report.startNew": "Start New Assessment",
    "report.loading": "Loading report...",
    "report.error": "Report not found.",
    "report.summary": "Executive Summary",
    "report.section.business": "Business Analysis",
    "report.section.operational": "Operational Analysis",
    "report.section.technology": "Technology Analysis",
    "report.section.aiReadiness": "AI Readiness",
    "report.section.recoSummary": "Recommendations Summary",
    "report.section.nextSteps": "Next Steps",
    "report.reco": "Recommendations",
    "report.impact": "Impact",
    "priority.HIGH": "High Priority",
    "priority.MEDIUM": "Medium Priority",
    "priority.LOW": "Low Priority",
    "property.title": "Property Profile",
    "property.name": "Name",
    "property.type": "Type",
    "property.location": "Location",
    "property.stage": "Business Stage",
    "property.units": "Units",
    "loading.title": "Generating Report",
    "loading.message": "LIA is analyzing your assessment results...",
    "loading.retry": "Try again",
    "loading.notFound": "Assessment not found.",
    "loading.error": "Failed to generate report.",
    "error.generic": "Something went wrong. Please try again.",
    "notfound.message": "Page not found.",
    "notfound.back": "Back to home",
  },
};

interface I18nValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string) => string;
}

const I18nContext = createContext<I18nValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  // Always start at the default so server and first client render match; the
  // stored preference is applied after mount (like next-themes).
  const [locale, setLocaleState] = useState<Locale>(DEFAULT_LOCALE);

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored === "id" || stored === "en") setLocaleState(stored);
  }, []);

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next);
    window.localStorage.setItem(STORAGE_KEY, next);
  }, []);

  const t = useCallback(
    (key: string) => dictionaries[locale][key] ?? dictionaries[DEFAULT_LOCALE][key] ?? key,
    [locale],
  );

  const value = useMemo(() => ({ locale, setLocale, t }), [locale, setLocale, t]);
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nValue {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}
