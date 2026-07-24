"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { FieldBuilder } from "@/components/admin/FieldBuilder";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { adminApi, type TemplateDetail, type TemplateWrite } from "@/lib/adminApi";

const inputClass =
  "rounded-md border border-navy/20 bg-white px-2 py-1 text-sm text-navy focus:border-gold focus:outline-none";

function emptyTemplate(): TemplateWrite {
  return {
    name: "",
    description: "",
    is_default: false,
    config: { knowledge: "", style: "", language: "id", fields: [] },
  };
}

export function TemplateForm({ existing }: { existing?: TemplateDetail }) {
  const router = useRouter();
  const [form, setForm] = useState<TemplateWrite>(
    existing
      ? {
          name: existing.name,
          description: existing.description ?? "",
          is_default: existing.is_default,
          config: existing.config,
        }
      : emptyTemplate(),
  );
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const patchConfig = (patch: Partial<TemplateWrite["config"]>) =>
    setForm((f) => ({ ...f, config: { ...f.config, ...patch } }));

  const save = async () => {
    setSaving(true);
    setError(null);
    try {
      if (existing) await adminApi.updateTemplate(existing.id, form);
      else await adminApi.createTemplate(form);
      router.push("/admin/templates");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Gagal menyimpan template.");
      setSaving(false);
    }
  };

  return (
    <div className="max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold text-navy">
        {existing ? "Edit Template" : "Template Baru"}
      </h1>

      <div className="grid gap-3 sm:grid-cols-2">
        <label className="space-y-1 text-sm">
          <span className="text-navy/60">Nama</span>
          <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        </label>
        <label className="space-y-1 text-sm">
          <span className="text-navy/60">Bahasa</span>
          <select
            value={form.config.language}
            onChange={(e) => patchConfig({ language: e.target.value as "id" | "en" })}
            className={`${inputClass} block w-full`}
          >
            <option value="id">id</option>
            <option value="en">en</option>
          </select>
        </label>
      </div>

      <label className="block space-y-1 text-sm">
        <span className="text-navy/60">Deskripsi</span>
        <Input
          value={form.description ?? ""}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
      </label>

      <label className="flex items-center gap-2 text-sm text-navy/70">
        <input
          type="checkbox"
          checked={form.is_default}
          onChange={(e) => setForm({ ...form, is_default: e.target.checked })}
        />
        Jadikan template default
      </label>

      <label className="block space-y-1 text-sm">
        <span className="text-navy/60">Knowledge (konteks domain)</span>
        <Textarea
          rows={3}
          value={form.config.knowledge}
          onChange={(e) => patchConfig({ knowledge: e.target.value })}
        />
      </label>

      <label className="block space-y-1 text-sm">
        <span className="text-navy/60">Style (persona / gaya)</span>
        <Textarea
          rows={3}
          value={form.config.style}
          onChange={(e) => patchConfig({ style: e.target.value })}
        />
      </label>

      <div className="space-y-2">
        <h2 className="text-sm font-semibold text-navy">Fields</h2>
        <FieldBuilder
          fields={form.config.fields}
          onChange={(fields) => patchConfig({ fields })}
        />
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex gap-2">
        <Button onClick={save} loading={saving}>
          Simpan
        </Button>
        <Button variant="secondary" onClick={() => router.push("/admin/templates")}>
          Batal
        </Button>
      </div>
    </div>
  );
}
