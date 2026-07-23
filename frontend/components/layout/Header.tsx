import Link from "next/link";

import { LanguageToggle } from "@/components/ui/LanguageToggle";
import { PageContainer } from "./PageContainer";

/** Global top bar with the Lightrees wordmark and the language switch. */
export function Header() {
  return (
    <header className="border-b border-navy/10">
      <PageContainer className="flex h-14 items-center justify-between">
        <Link href="/" className="text-base font-semibold tracking-tight text-navy">
          Lightrees
        </Link>
        <LanguageToggle />
      </PageContainer>
    </header>
  );
}
