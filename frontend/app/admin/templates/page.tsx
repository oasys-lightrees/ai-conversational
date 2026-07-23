"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { adminApi, type TemplateSummary } from "@/lib/adminApi";

export default function AdminTemplatesPage() {
  const [templates, setTemplates] = useState<TemplateSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    adminApi
      .listTemplates()
      .then(setTemplates)
      .catch((e) => setError(e instanceof Error ? e.message : "Gagal memuat template."));
  }, []);

  useEffect(load, [load]);

  const clone = async (id: string) => {
    await adminApi.cloneTemplate(id);
    load();
  };
  const setDefault = async (id: string) => {
    await adminApi.setDefaultTemplate(id);
    load();
  };
  const remove = async (id: string) => {
    try {
      await adminApi.deleteTemplate(id);
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Gagal menghapus.");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-navy">Templates</h1>
        <Link href="/admin/templates/new">
          <Button>Template Baru</Button>
        </Link>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {!templates ? (
        <Spinner />
      ) : (
        <div className="overflow-hidden rounded-xl border border-navy/10">
          <table className="w-full text-sm">
            <thead className="bg-navy/5 text-left text-navy/60">
              <tr>
                <th className="px-4 py-2 font-medium">Nama</th>
                <th className="px-4 py-2 font-medium">Bahasa</th>
                <th className="px-4 py-2 font-medium">Default</th>
                <th className="px-4 py-2" />
              </tr>
            </thead>
            <tbody>
              {templates.map((t) => (
                <tr key={t.id} className="border-t border-navy/10">
                  <td className="px-4 py-2">
                    <Link href={`/admin/templates/${t.id}`} className="font-medium text-navy hover:underline">
                      {t.name}
                    </Link>
                    {t.description && <div className="text-xs text-navy/50">{t.description}</div>}
                  </td>
                  <td className="px-4 py-2 uppercase text-navy/70">{t.language}</td>
                  <td className="px-4 py-2">{t.is_default && <Badge>Default</Badge>}</td>
                  <td className="px-4 py-2">
                    <div className="flex justify-end gap-2">
                      {!t.is_default && (
                        <Button variant="ghost" onClick={() => setDefault(t.id)} className="px-2 py-1 text-xs">
                          Jadikan Default
                        </Button>
                      )}
                      <Button variant="ghost" onClick={() => clone(t.id)} className="px-2 py-1 text-xs">
                        Duplikat
                      </Button>
                      <Button variant="ghost" onClick={() => remove(t.id)} className="px-2 py-1 text-xs">
                        Hapus
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
