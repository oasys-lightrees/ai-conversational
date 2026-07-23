import type { AssessmentData } from "@/lib/api";
import { getNumber, getString, humanizeEnum } from "@/lib/labels";

/** Key facts about the assessed property, derived from assessment_data. */
export function PropertySummaryCard({ data }: { data: AssessmentData }) {
  const rows: Array<[string, string]> = [];

  const name = getString(data, "property_name");
  if (name) rows.push(["Nama", name]);

  const type = getString(data, "property_type");
  if (type) rows.push(["Jenis", humanizeEnum(type)]);

  const location = getString(data, "property_location");
  if (location) rows.push(["Lokasi", location]);

  const stage = getString(data, "business_stage");
  if (stage) rows.push(["Tahap Bisnis", humanizeEnum(stage)]);

  const units = getNumber(data, "total_units");
  if (units != null) rows.push(["Jumlah Unit", String(units)]);

  if (rows.length === 0) return null;

  return (
    <section className="rounded-xl border border-slate-200 p-5 dark:border-slate-800">
      <h2 className="mb-3 text-sm font-semibold text-slate-900 dark:text-slate-100">
        Profil Properti
      </h2>
      <dl className="space-y-2 text-sm">
        {rows.map(([label, value]) => (
          <div key={label} className="flex justify-between gap-4">
            <dt className="text-slate-500 dark:text-slate-400">{label}</dt>
            <dd className="text-right text-slate-900 dark:text-slate-100">{value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
