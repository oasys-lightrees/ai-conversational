// Maps backend conversation-stage codes (StateService.current_stage) to
// Bahasa Indonesia labels for the progress header.

const STAGE_LABELS: Record<string, string> = {
  PROPERTY_PROFILE: "Profil Properti",
  BUSINESS_STAGE: "Tahap Bisnis",
  BRANCH: "Detail Bisnis",
  OPERATIONS: "Operasional",
  TECHNOLOGY: "Teknologi",
  PAIN_POINTS: "Tantangan",
  GOALS: "Tujuan",
  COMPLETE: "Selesai",
};

export function stageLabel(stage: string | null): string {
  if (!stage) return "Asesmen";
  return STAGE_LABELS[stage] ?? stage;
}
