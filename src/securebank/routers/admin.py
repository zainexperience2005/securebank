from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from securebank.database import get_db
from securebank.dependencies import require_admin
from securebank.models import AuditLog, User
from securebank.schemas import AuditLogResponse

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get(
    "/audit-logs",
    response_model=list[AuditLogResponse],
)
def get_audit_logs(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    logs = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc())).all()

    return logs
