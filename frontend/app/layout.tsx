import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { I18nProvider } from "@/lib/i18n";

export const metadata: Metadata = {
  title: "AI Conversational Assessment Agent",
  description:
    "Conversational business assessment for property owners, powered by AI.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id" suppressHydrationWarning>
      <body className="bg-white text-navy antialiased">
        <ThemeProvider attribute="class" defaultTheme="light" forcedTheme="light">
          <I18nProvider>{children}</I18nProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
