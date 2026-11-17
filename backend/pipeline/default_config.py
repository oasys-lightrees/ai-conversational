"""The default pipeline configuration.

The hospitality schema used when no template is selected.

Requiredness drives the conversation: ``StateService`` only reports currently
*required* fields as missing, and Prompt 3 is forbidden from straying off the
missing list (see ``chat_service._next_question_system``). An optional field is
therefore never asked about, so every field the assessment is expected to
collect is marked ``required`` (or ``required_when`` where it only applies in
context, like ``pms_name``). Leave a field optional only if it is genuinely
fine for it to stay empty forever.
"""

from __future__ import annotations

from backend.pipeline.config import FieldSpec, PipelineConfig

_PROPERTY_TYPES = [
    "VILLA",
    "HOTEL",
    "APARTMENT",
    "BOARDING_HOUSE",
    "GUEST_HOUSE",
    "RESORT",
    "COMMERCIAL_BUILDING",
    "OTHER",
]
_OWNERSHIP = ["OWNED", "LEASED", "MANAGED", "OTHER"]
_STAGES = ["PLANNING", "IDLE_PROPERTY", "UNDERPERFORMING", "OPERATING_SUCCESSFULLY"]
_PROCESS = ["MANUAL", "SEMI_DIGITAL", "FULLY_DIGITAL"]

DEFAULT_KNOWLEDGE = (
    "Domain: hospitality property businesses in Indonesia — villas, hotels, "
    "guest houses, boarding houses (kos), resorts, and commercial buildings."
)
DEFAULT_STYLE = (
    "You are LIA, a friendly and concise assistant. Keep the conversation "
    "natural, ask one question at a time, and never invent information."
)

DEFAULT_CONFIG = PipelineConfig(
    knowledge=DEFAULT_KNOWLEDGE,
    style=DEFAULT_STYLE,
    language="id",
    fields=[
        # --- Property profile ---
        FieldSpec(name="property_name", label="Nama Properti", type="string", required=True, section="PROPERTY_PROFILE"),
        FieldSpec(
            name="property_type",
            label="Jenis Properti",
            type="enum",
            enum_options=_PROPERTY_TYPES,
            required=True,
            section="PROPERTY_PROFILE",
        ),
        FieldSpec(
            name="property_location",
            label="Lokasi",
            type="string",
            aliases=["location"],
            required=True,
            section="PROPERTY_PROFILE",
        ),
        FieldSpec(name="ownership_type", label="Kepemilikan", type="enum", enum_options=_OWNERSHIP, required=True, section="PROPERTY_PROFILE"),
        FieldSpec(name="total_units", label="Jumlah Unit", type="integer", required=True, section="PROPERTY_PROFILE"),
        # --- Business stage ---
        FieldSpec(
            name="business_stage",
            label="Tahap Bisnis",
            type="enum",
            enum_options=_STAGES,
            required=True,
            section="BUSINESS_STAGE",
        ),
        # --- Branch (stage-specific) ---
        FieldSpec(name="occupancy_rate", label="Tingkat Hunian", type="decimal", required_when={"business_stage": ["UNDERPERFORMING"]}, section="BRANCH"),
        FieldSpec(name="monthly_revenue", label="Pendapatan Bulanan", type="decimal", required_when={"business_stage": ["UNDERPERFORMING"]}, section="BRANCH"),
        FieldSpec(name="average_room_rate", label="Tarif Rata-rata", type="decimal", required_when={"business_stage": ["UNDERPERFORMING"]}, section="BRANCH"),
        FieldSpec(name="booking_platforms", label="Platform Booking", type="list", aliases=["booking_channels"], required_when={"business_stage": ["UNDERPERFORMING"]}, section="BRANCH"),
        FieldSpec(name="target_launch_date", label="Target Peluncuran", type="string", required_when={"business_stage": ["PLANNING", "IDLE_PROPERTY"]}, section="BRANCH"),
        FieldSpec(name="investment_budget", label="Anggaran Investasi", type="integer", required_when={"business_stage": ["PLANNING"]}, section="BRANCH"),
        FieldSpec(name="reason_not_operating", label="Alasan Belum Beroperasi", type="string", required_when={"business_stage": ["IDLE_PROPERTY"]}, section="BRANCH"),
        FieldSpec(name="main_obstacle", label="Kendala Utama", type="string", required_when={"business_stage": ["IDLE_PROPERTY"]}, section="BRANCH"),
        FieldSpec(name="expansion_plan", label="Rencana Ekspansi", type="string", required_when={"business_stage": ["OPERATING_SUCCESSFULLY"]}, section="BRANCH"),
        FieldSpec(name="automation_interest", label="Minat Otomasi", type="string", required_when={"business_stage": ["OPERATING_SUCCESSFULLY"]}, section="BRANCH"),
        # --- Operations ---
        FieldSpec(name="staff_count", label="Jumlah Staf", type="integer", required=True, section="OPERATIONS"),
        FieldSpec(name="check_in_process", label="Proses Check-in", type="enum", enum_options=_PROCESS, required=True, section="OPERATIONS"),
        FieldSpec(name="housekeeping_process", label="Proses Housekeeping", type="enum", enum_options=_PROCESS, required=True, section="OPERATIONS"),
        FieldSpec(name="maintenance_process", label="Proses Pemeliharaan", type="enum", enum_options=_PROCESS, required=True, section="OPERATIONS"),
        FieldSpec(name="complaint_handling", label="Penanganan Keluhan", type="enum", enum_options=_PROCESS, required=True, section="OPERATIONS"),
        # --- Technology ---
        FieldSpec(name="uses_pms", label="Menggunakan PMS", type="boolean", required=True, section="TECHNOLOGY"),
        FieldSpec(name="pms_name", label="Nama PMS", type="string", required_when={"uses_pms": ["true"]}, section="TECHNOLOGY"),
        FieldSpec(name="accounting_system", label="Sistem Akuntansi", type="string", required=True, section="TECHNOLOGY"),
        FieldSpec(name="communication_channels", label="Kanal Komunikasi", type="list", required=True, section="TECHNOLOGY"),
        # --- Pain points & goals ---
        FieldSpec(name="pain_points", label="Tantangan", type="list", required=True, section="PAIN_POINTS"),
        FieldSpec(name="business_goals", label="Tujuan Bisnis", type="list", required=True, section="GOALS"),
    ],
)
