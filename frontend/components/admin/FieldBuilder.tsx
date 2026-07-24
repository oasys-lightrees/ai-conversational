"use client";

import { ChevronDown, ChevronUp, Plus, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { type FieldSpec, type FieldType } from "@/lib/adminApi";
import { cn } from "@/lib/utils";

const TYPES: FieldType[] = ["string", "integer", "decimal", "boolean", "list", "enum"];

const inputClass =
  "rounded-md border border-navy/20 bg-white px-2 py-1 text-sm text-navy focus:border-gold focus:outline-none";

/** Editor for a template's list of FieldSpecs. */
export function FieldBuilder({
  fields,
  onChange,
}: {
  fields: FieldSpec[];
  onChange: (fields: FieldSpec[]) => void;
}) {
  const update = (index: number, patch: Partial<FieldSpec>) => {
    onChange(fields.map((f, i) => (i === index ? { ...f, ...patch } : f)));
  };
  const remove = (index: number) => onChange(fields.filter((_, i) => i !== index));
  const move = (index: number, delta: number) => {
    const target = index + delta;
    if (target < 0 || target >= fields.length) return;
    const next = [...fields];
    [next[index], next[target]] = [next[target], next[index]];
    onChange(next);
  };
  const add = () =>
    onChange([...fields, { name: "", type: "string", required: false, section: "" }]);

  return (
    <div className="space-y-3">
      {fields.map((field, index) => (
        <div key={index} className="rounded-lg border border-navy/10 p-3">
          <div className="flex flex-wrap items-center gap-2">
            <Input
              value={field.name}
              onChange={(e) => update(index, { name: e.target.value })}
              placeholder="nama_field"
              className="max-w-[180px]"
            />
            <select
              value={field.type}
              onChange={(e) => update(index, { type: e.target.value as FieldType })}
              className={inputClass}
            >
              {TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
            <Input
              value={field.section ?? ""}
              onChange={(e) => update(index, { section: e.target.value })}
              placeholder="section"
              className="max-w-[140px]"
            />
            <label className="flex items-center gap-1 text-sm text-navy/70">
              <input
                type="checkbox"
                checked={Boolean(field.required)}
                onChange={(e) => update(index, { required: e.target.checked })}
              />
              required
            </label>
            <div className="ml-auto flex items-center gap-1">
              <button type="button" onClick={() => move(index, -1)} aria-label="Naik" className="p-1 text-navy/50 hover:text-navy">
                <ChevronUp className="h-4 w-4" />
              </button>
              <button type="button" onClick={() => move(index, 1)} aria-label="Turun" className="p-1 text-navy/50 hover:text-navy">
                <ChevronDown className="h-4 w-4" />
              </button>
              <button type="button" onClick={() => remove(index)} aria-label="Hapus field" className="p-1 text-red-500 hover:text-red-700">
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </div>

          <div className="mt-2 flex flex-wrap gap-2">
            <Input
              value={field.label ?? ""}
              onChange={(e) => update(index, { label: e.target.value })}
              placeholder="label"
              className="max-w-[180px]"
            />
            <Input
              value={field.description ?? ""}
              onChange={(e) => update(index, { description: e.target.value })}
              placeholder="deskripsi (petunjuk ekstraksi)"
              className="flex-1"
            />
          </div>

          {field.type === "enum" && (
            <Input
              value={(field.enum_options ?? []).join(", ")}
              onChange={(e) =>
                update(index, {
                  enum_options: e.target.value
                    .split(",")
                    .map((s) => s.trim())
                    .filter(Boolean),
                })
              }
              placeholder="opsi enum, dipisah koma (mis. VILLA, HOTEL)"
              className={cn("mt-2 w-full")}
            />
          )}
        </div>
      ))}

      <Button variant="secondary" onClick={add}>
        <Plus className="h-4 w-4" />
        Tambah Field
      </Button>
    </div>
  );
}
