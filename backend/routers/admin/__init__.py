"""Admin API — template management, assessments browsing, and metrics.

All routes are gated by :func:`require_admin` (shared-key bearer auth). See
``docs/12-admin-dashboard.MD``.
"""

from fastapi import APIRouter, Depends

from backend.routers.admin.auth import require_admin
from backend.routers.admin.assessments import router as assessments_router
from backend.routers.admin.metrics import router as metrics_router
from backend.routers.admin.templates import router as templates_router

# Single admin router; every included sub-router inherits the auth dependency.
router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])
router.include_router(templates_router)
router.include_router(assessments_router)
router.include_router(metrics_router)

__all__ = ["router", "require_admin"]
