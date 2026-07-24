"use client";

import { usePathname } from "next/navigation";

import { AdminGuard } from "@/components/admin/AdminGuard";
import { Sidebar } from "@/components/admin/Sidebar";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLogin = pathname === "/admin/login";

  return (
    <AdminGuard>
      {isLogin ? (
        children
      ) : (
        <div className="flex min-h-screen bg-white">
          <Sidebar />
          <main className="flex-1 overflow-x-auto p-8">{children}</main>
        </div>
      )}
    </AdminGuard>
  );
}
