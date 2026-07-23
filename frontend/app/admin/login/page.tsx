"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { adminApi } from "@/lib/adminApi";
import { setAdminKey } from "@/lib/adminAuth";

export default function AdminLoginPage() {
  const router = useRouter();
  const [key, setKey] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!key.trim()) return;
    setLoading(true);
    setError(null);
    setAdminKey(key.trim());
    try {
      await adminApi.metrics(); // validates the key
      router.replace("/admin");
    } catch {
      setError("Kunci admin tidak valid.");
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-white p-8">
      <div className="w-full max-w-sm space-y-4 rounded-xl border border-navy/10 p-6">
        <h1 className="text-lg font-semibold text-navy">Admin Login</h1>
        <p className="text-sm text-navy/60">Masukkan kunci admin untuk melanjutkan.</p>
        <Input
          type="password"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="ADMIN_API_KEY"
          autoFocus
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <Button onClick={submit} loading={loading} className="w-full">
          Masuk
        </Button>
      </div>
    </main>
  );
}
