"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { adminApi, type PaginatedAssessments } from "@/lib/adminApi";
import { cn } from "@/lib/utils";

const STATUSES = ["", "IN_PROGRESS", "COMPLETED", "ABANDONED"];

export default function AdminAssessmentsPage() {
  const [data, setData] = useState<PaginatedAssessments | null>(null);
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setData(null);
    adminApi
      .listAssessments({ status: status || undefined, page })
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "Gagal memuat."));
  }, [status, page]);

  useEffect(load, [load]);

  const pages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-navy">Assessments</h1>

      <div className="flex flex-wrap gap-2">
        {STATUSES.map((s) => (
          <button
            key={s || "ALL"}
            onClick={() => {
              setStatus(s);
              setPage(1);
            }}
            className={cn(
              "rounded-lg px-3 py-1 text-sm",
              status === s ? "bg-navy text-white" : "bg-navy/5 text-navy hover:bg-navy/10",
            )}
          >
            {s || "SEMUA"}
          </button>
        ))}
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {!data ? (
        <Spinner />
      ) : (
        <>
          <div className="overflow-hidden rounded-xl border border-navy/10">
            <table className="w-full text-sm">
              <thead className="bg-navy/5 text-left text-navy/60">
                <tr>
                  <th className="px-4 py-2 font-medium">ID</th>
                  <th className="px-4 py-2 font-medium">Status</th>
                  <th className="px-4 py-2 font-medium">Progress</th>
                  <th className="px-4 py-2 font-medium">Dibuat</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((a) => (
                  <tr key={a.assessment_id} className="border-t border-navy/10">
                    <td className="px-4 py-2">
                      <Link
                        href={`/admin/assessments/${a.assessment_id}`}
                        className="font-mono text-xs text-navy hover:underline"
                      >
                        {a.assessment_id.slice(0, 8)}
                      </Link>
                    </td>
                    <td className="px-4 py-2 text-navy/70">{a.status}</td>
                    <td className="px-4 py-2">{a.completion_percentage}%</td>
                    <td className="px-4 py-2 text-navy/60">
                      {new Date(a.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
                {data.items.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-4 py-6 text-center text-navy/50">
                      Tidak ada asesmen.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between text-sm text-navy/60">
            <span>{data.total} total</span>
            <div className="flex items-center gap-2">
              <Button variant="ghost" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                Sebelumnya
              </Button>
              <span>
                {page} / {pages}
              </span>
              <Button variant="ghost" disabled={page >= pages} onClick={() => setPage((p) => p + 1)}>
                Berikutnya
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
