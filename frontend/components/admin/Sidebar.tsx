"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { BarChart3, FileText, LayoutDashboard, LogOut } from "lucide-react";

import { clearAdminKey } from "@/lib/adminAuth";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/admin", label: "Overview", icon: LayoutDashboard },
  { href: "/admin/templates", label: "Templates", icon: FileText },
  { href: "/admin/assessments", label: "Assessments", icon: BarChart3 },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  const logout = () => {
    clearAdminKey();
    router.replace("/admin/login");
  };

  const isActive = (href: string) =>
    href === "/admin" ? pathname === "/admin" : pathname.startsWith(href);

  return (
    <aside className="flex w-56 shrink-0 flex-col border-r border-navy/10 bg-white">
      <div className="flex h-14 items-center border-b border-navy/10 px-4">
        <Link href="/admin" className="font-semibold text-navy">
          Lightrees Admin
        </Link>
      </div>
      <nav className="flex-1 space-y-1 p-3">
        {NAV.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              isActive(href) ? "bg-navy text-white" : "text-navy hover:bg-navy/5",
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>
      <button
        onClick={logout}
        className="flex items-center gap-2 border-t border-navy/10 px-5 py-3 text-sm text-navy/70 hover:bg-navy/5"
      >
        <LogOut className="h-4 w-4" />
        Keluar
      </button>
    </aside>
  );
}
