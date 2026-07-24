"""Configurable AI-pipeline domain: config objects, the default config, and the
config-driven field mapper. See ``docs/11-pipeline-config.MD``."""

from backend.pipeline.config import FieldSpec, PipelineConfig
from backend.pipeline.default_config import DEFAULT_CONFIG
from backend.pipeline.mapper import FieldMapper

__all__ = ["FieldSpec", "PipelineConfig", "DEFAULT_CONFIG", "FieldMapper"]
