import Link from "next/link";

import { PageContainer } from "./PageContainer";

/** Global top bar with the Lightrees wordmark. */
export function Header() {
  return (
    <header className="border-b border-navy/10">
      <PageContainer className="flex h-14 items-center">
        <Link href="/" className="text-base font-semibold tracking-tight text-navy">
          Lightrees
        </Link>
      </PageContainer>
    </header>
  );
}
