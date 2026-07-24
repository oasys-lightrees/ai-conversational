"use client";

import { useEffect, useState, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";

import { getAdminKey } from "@/lib/adminAuth";

/** Redirects to /admin/login when no admin key is stored (login page exempt). */
export function AdminGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [checked, setChecked] = useState(false);

  const isLogin = pathname === "/admin/login";

  useEffect(() => {
    if (isLogin) {
      setChecked(true);
      return;
    }
    if (!getAdminKey()) {
      router.replace("/admin/login");
      return;
    }
    setChecked(true);
  }, [isLogin, router]);

  if (!checked) return null;
  return <>{children}</>;
}
