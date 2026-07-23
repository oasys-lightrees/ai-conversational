import Link from "next/link";

import { PageContainer } from "./PageContainer";

/** Global top bar with the Lightrees wordmark. */
export function Header() {
  return (
    <header className="border-b border-slate-200 dark:border-slate-800">
      <PageContainer className="flex h-14 items-center">
        <Link
          href="/"
          className="text-base font-semibold tracking-tight text-slate-900 dark:text-slate-100"
        >
          Lightrees
        </Link>
      </PageContainer>
    </header>
  );
}
