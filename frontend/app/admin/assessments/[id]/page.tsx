"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { ChatBubble } from "@/components/chat/ChatBubble";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { adminApi, type AssessmentDetail } from "@/lib/adminApi";

export default function AdminAssessmentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [detail, setDetail] = useState<AssessmentDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    adminApi
      .getAssessment(id)
      .then(setDetail)
      .catch((e) => setError(e instanceof Error ? e.message : "Gagal memuat."));
  }, [id]);

  const remove = async () => {
    await adminApi.deleteAssessment(id);
    router.push("/admin/assessments");
  };

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!detail) return <Spinner />;

  const dataRows = Object.entries(detail.assessment_data);

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-navy">Asesmen</h1>
        <Button variant="secondary" onClick={remove}>
          Hapus
        </Button>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-xl border border-navy/10 p-3">
          <div className="text-xs text-navy/50">Status</div>
          <div className="font-medium text-navy">{detail.status}</div>
        </div>
        <div className="rounded-xl border border-navy/10 p-3">
          <div className="text-xs text-navy/50">Progress</div>
          <div className="font-medium text-navy">{detail.completion_percentage}%</div>
        </div>
        <div className="rounded-xl border border-navy/10 p-3">
          <div className="text-xs text-navy/50">Dibuat</div>
          <div className="text-sm text-navy">{new Date(detail.created_at).toLocaleString()}</div>
        </div>
      </div>

      <section className="space-y-2">
        <h2 className="text-sm font-semibold text-navy">Data Terkumpul</h2>
        {dataRows.length === 0 ? (
          <p className="text-sm text-navy/50">Belum ada data.</p>
        ) : (
          <dl className="rounded-xl border border-navy/10 p-4 text-sm">
            {dataRows.map(([k, v]) => (
              <div key={k} className="flex justify-between gap-4 border-b border-navy/5 py-1 last:border-0">
                <dt className="text-navy/60">{k}</dt>
                <dd className="text-right text-navy">{JSON.stringify(v)}</dd>
              </div>
            ))}
          </dl>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold text-navy">Percakapan</h2>
        {detail.conversation.length === 0 ? (
          <p className="text-sm text-navy/50">Belum ada percakapan.</p>
        ) : (
          <div className="space-y-3">
            {detail.conversation.map((m, i) => (
              <ChatBubble key={i} role={m.role}>
                {m.message}
              </ChatBubble>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
