"use client";

import { useEffect, useState } from "react";

import { api, type TemplateSummary } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { setPendingTemplateId } from "@/lib/session";

/** Lets the user choose which template a new assessment uses.

Hidden when there is 0–1 template (nothing to choose). The selection is stored
and consumed by the next fresh start in useAssessment. */
export function TemplatePicker() {
  const { t } = useI18n();
  const [templates, setTemplates] = useState<TemplateSummary[]>([]);
  const [selected, setSelected] = useState("");

  useEffect(() => {
    api
      .getTemplates()
      .then((list) => {
        setTemplates(list);
        const preferred = list.find((tpl) => tpl.is_default) ?? list[0];
        if (preferred) {
          setSelected(preferred.id);
          setPendingTemplateId(preferred.id);
        }
      })
      .catch(() => {
        /* no picker if templates can't be loaded — backend uses its default */
      });
  }, []);

  if (templates.length <= 1) return null;

  return (
    <label className="flex flex-col items-center gap-1.5 text-sm">
      <span className="text-navy/60">{t("start.template")}</span>
      <select
        value={selected}
        onChange={(e) => {
          setSelected(e.target.value);
          setPendingTemplateId(e.target.value);
        }}
        className="rounded-lg border border-navy/20 bg-white px-3 py-2 text-navy focus:border-gold focus:outline-none focus:ring-2 focus:ring-gold/30"
      >
        {templates.map((tpl) => (
          <option key={tpl.id} value={tpl.id}>
            {tpl.name}
          </option>
        ))}
      </select>
    </label>
  );
}
