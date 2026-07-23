// Landing page (route: /). See docs/frontend/05-page-specification.MD — Page 1.

import { ClipboardList, MessagesSquare, Sparkles } from "lucide-react";

import { FeatureCard } from "@/components/landing/FeatureCard";
import { StartCta } from "@/components/landing/StartCta";
import { Footer } from "@/components/layout/Footer";
import { Header } from "@/components/layout/Header";
import { PageContainer } from "@/components/layout/PageContainer";

const FEATURES = [
  {
    icon: MessagesSquare,
    title: "Percakapan Natural",
    description: "Jawab pertanyaan LIA seperti mengobrol biasa — tanpa formulir panjang.",
  },
  {
    icon: ClipboardList,
    title: "Analisis Terstruktur",
    description: "Informasi bisnis Anda diekstrak dan dinilai secara otomatis.",
  },
  {
    icon: Sparkles,
    title: "Rekomendasi AI",
    description: "Terima laporan dan rekomendasi yang dipersonalisasi untuk properti Anda.",
  },
];

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <PageContainer className="flex flex-col items-center gap-10 py-16 text-center">
          <div className="space-y-4">
            <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Asesmen Bisnis Properti berbasis AI
            </h1>
            <p className="mx-auto max-w-xl text-navy/70">
              Nilai bisnis properti Anda melalui percakapan natural dan terima
              rekomendasi berbasis AI dari LIA.
            </p>
          </div>

          <StartCta />

          <div className="grid w-full gap-4 sm:grid-cols-3">
            {FEATURES.map((feature) => (
              <FeatureCard key={feature.title} {...feature} />
            ))}
          </div>
        </PageContainer>
      </main>
      <Footer />
    </div>
  );
}
