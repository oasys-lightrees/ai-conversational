"use client";

import type { AssessmentData } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { getNumber, getString, humanizeEnum } from "@/lib/labels";

/** Key facts about the assessed property, derived from assessment_data. */
export function PropertySummaryCard({ data }: { data: AssessmentData }) {
  const { t } = useI18n();
  const rows: Array<[string, string]> = [];

  const name = getString(data, "property_name");
  if (name) rows.push([t("property.name"), name]);

  const type = getString(data, "property_type");
  if (type) rows.push([t("property.type"), humanizeEnum(type)]);

  const location = getString(data, "property_location");
  if (location) rows.push([t("property.location"), location]);

  const stage = getString(data, "business_stage");
  if (stage) rows.push([t("property.stage"), humanizeEnum(stage)]);

  const units = getNumber(data, "total_units");
  if (units != null) rows.push([t("property.units"), String(units)]);

  if (rows.length === 0) return null;

  return (
    <section className="rounded-xl bg-ink p-5 text-white">
      <h2 className="mb-3 text-sm font-semibold text-white">{t("property.title")}</h2>
      <dl className="space-y-2 text-sm">
        {rows.map(([label, value]) => (
          <div key={label} className="flex justify-between gap-4">
            <dt className="text-white/60">{label}</dt>
            <dd className="text-right text-white">{value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
