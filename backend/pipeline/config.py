"""Runtime configuration objects for the AI pipeline.

A :class:`PipelineConfig` parameterizes the whole pipeline — the domain
``knowledge`` and ``style`` injected into prompts, the response ``language``, and
the ``fields`` to extract. Services consume a config instead of hardcoded
constants. Configs are plain pydantic models so they serialize cleanly to/from
the JSON snapshot stored on an assessment. See ``docs/11-pipeline-config.MD``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

FieldType = Literal["string", "integer", "decimal", "boolean", "list", "enum"]


class FieldSpec(BaseModel):
    """One collectable field."""

    name: str
    label: str = ""
    description: str = ""
    type: FieldType = "string"
    enum_options: list[str] = Field(default_factory=list)
    # Alternative input keys the model might emit (e.g. "location").
    aliases: list[str] = Field(default_factory=list)
    # Always required.
    required: bool = False
    # Conditionally required: required if, for every (field -> values) entry,
    # the current state's value for `field` is one of `values`.
    required_when: dict[str, list[str]] | None = None
    # Grouping / conversation stage.
    section: str = ""

    def is_required(self, state: dict) -> bool:
        if self.required:
            return True
        if self.required_when:
            return all(
                str(state.get(field)) in [str(v) for v in values]
                for field, values in self.required_when.items()
            )
        return False


class PipelineConfig(BaseModel):
    """The full configuration a pipeline run operates against."""

    knowledge: str = ""
    style: str = ""
    language: Literal["id", "en"] = "id"
    fields: list[FieldSpec] = Field(default_factory=list)

    def field_names(self) -> list[str]:
        return [field.name for field in self.fields]
