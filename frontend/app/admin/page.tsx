"use client";

import { useEffect, useState } from "react";

import { BarList, MetricCard } from "@/components/admin/MetricCard";
import { Spinner } from "@/components/ui/spinner";
import { adminApi, type Metrics } from "@/lib/adminApi";

export default function AdminOverviewPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    adminApi
      .metrics()
      .then(setMetrics)
      .catch((e) => setError(e instanceof Error ? e.message : "Gagal memuat metrik."));
  }, []);

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!metrics) return <Spinner />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-navy">Overview</h1>

      <div className="grid grid-cols-3 gap-4">
        <MetricCard label="Total Asesmen" value={metrics.total_assessments} />
        <MetricCard label="Selesai" value={metrics.by_status.COMPLETED ?? 0} />
        <MetricCard
          label="Tingkat Selesai"
          value={`${Math.round(metrics.completion_rate * 100)}%`}
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <BarList title="Berdasarkan Jenis Properti" items={metrics.by_property_type} />
        <BarList title="Berdasarkan Tahap Bisnis" items={metrics.by_business_stage} />
        <BarList
          title="Berdasarkan Status"
          items={Object.entries(metrics.by_status).map(([key, count]) => ({ key, count }))}
        />
      </div>
    </div>
  );
}
