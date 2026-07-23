"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { TemplateForm } from "@/components/admin/TemplateForm";
import { Spinner } from "@/components/ui/spinner";
import { adminApi, type TemplateDetail } from "@/lib/adminApi";

export default function EditTemplatePage() {
  const { id } = useParams<{ id: string }>();
  const [template, setTemplate] = useState<TemplateDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    adminApi
      .getTemplate(id)
      .then(setTemplate)
      .catch((e) => setError(e instanceof Error ? e.message : "Gagal memuat template."));
  }, [id]);

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!template) return <Spinner />;
  return <TemplateForm existing={template} />;
}
