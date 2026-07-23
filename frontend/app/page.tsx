"use client";

// Landing page (route: /). See docs/frontend/05-page-specification.MD — Page 1.

import { ClipboardList, MessagesSquare, Sparkles } from "lucide-react";

import { FeatureCard } from "@/components/landing/FeatureCard";
import { StartCta } from "@/components/landing/StartCta";
import { TemplatePicker } from "@/components/landing/TemplatePicker";
import { Footer } from "@/components/layout/Footer";
import { Header } from "@/components/layout/Header";
import { PageContainer } from "@/components/layout/PageContainer";
import { useI18n } from "@/lib/i18n";

export default function LandingPage() {
  const { t } = useI18n();

  const features = [
    { icon: MessagesSquare, title: t("feature.chat.title"), description: t("feature.chat.desc") },
    { icon: ClipboardList, title: t("feature.analysis.title"), description: t("feature.analysis.desc") },
    { icon: Sparkles, title: t("feature.reco.title"), description: t("feature.reco.desc") },
  ];

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <PageContainer className="flex flex-col items-center gap-10 py-16 text-center">
          <div className="space-y-4">
            <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">{t("hero.title")}</h1>
            <p className="mx-auto max-w-xl text-navy/70">{t("hero.subtitle")}</p>
          </div>

          <div className="flex flex-col items-center gap-4">
            <TemplatePicker />
            <StartCta />
          </div>

          <div className="grid w-full gap-4 sm:grid-cols-3">
            {features.map((feature) => (
              <FeatureCard key={feature.title} {...feature} />
            ))}
          </div>
        </PageContainer>
      </main>
      <Footer />
    </div>
  );
}
