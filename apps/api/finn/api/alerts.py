from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from finn.db.database import get_connection
from finn.alerts.engine import AlertEngine

router = APIRouter(tags=["Alerts & Notification Rules"])

class UpdateRulesRequest(BaseModel):
    price_pct: float = Field(..., ge=0.5, le=50.0, description="Price movement threshold percentage")
    volume_multiple: float = Field(..., ge=1.0, le=20.0, description="Volume multiple over 20-day mean")
    categories: List[str] = Field(..., description="Tracked category machine keys")
    min_materiality: str = Field(default="worth_a_look", description="Minimum tier: routine, worth_a_look, needs_attention")
    enabled: bool = Field(default=True)

class PreviewRulesRequest(BaseModel):
    price_pct: Optional[float] = None
    volume_multiple: Optional[float] = None
    categories: Optional[List[str]] = None
    min_materiality: Optional[str] = None

@router.get("/api/v1/notification-rules")
def get_notification_rules(request: Request) -> Dict[str, Any]:
    session_id = getattr(request.state, "session_id", "default_session")
    conn = get_connection()
    try:
        engine = AlertEngine(conn)
        rules = engine.get_or_create_rules(session_id)
        return {"data": rules}
    finally:
        conn.close()

@router.put("/api/v1/notification-rules")
def update_notification_rules(payload: UpdateRulesRequest, request: Request) -> Dict[str, Any]:
    session_id = getattr(request.state, "session_id", "default_session")
    conn = get_connection()
    try:
        engine = AlertEngine(conn)
        updated = engine.update_rules(
            session_id=session_id,
            price_pct=payload.price_pct,
            volume_multiple=payload.volume_multiple,
            categories=payload.categories,
            min_materiality=payload.min_materiality,
            enabled=payload.enabled
        )
        return {"data": updated, "message": "Notification rules updated successfully"}
    finally:
        conn.close()

@router.post("/api/v1/notification-rules/preview")
def preview_notification_rules(payload: PreviewRulesRequest, request: Request) -> Dict[str, Any]:
    session_id = getattr(request.state, "session_id", "default_session")
    conn = get_connection()
    try:
        engine = AlertEngine(conn)
        matches = engine.preview_rules(
            session_id=session_id,
            price_pct=payload.price_pct,
            volume_multiple=payload.volume_multiple,
            categories=payload.categories,
            min_materiality=payload.min_materiality
        )
        return {
            "data": matches,
            "meta": {
                "matched_count": len(matches),
                "is_preview": True,
                "note": "Preview results only; no notifications were added to inbox"
            }
        }
    finally:
        conn.close()

@router.get("/api/v1/alerts")
def get_alerts(request: Request) -> Dict[str, Any]:
    session_id = getattr(request.state, "session_id", "default_session")
    conn = get_connection()
    try:
        engine = AlertEngine(conn)
        res = engine.get_session_alerts(session_id)
        return res
    finally:
        conn.close()

@router.patch("/api/v1/alerts/{alert_id}")
def acknowledge_alert(alert_id: str, request: Request) -> Dict[str, Any]:
    session_id = getattr(request.state, "session_id", "default_session")
    conn = get_connection()
    try:
        engine = AlertEngine(conn)
        success = engine.acknowledge_alert(session_id, alert_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert '{alert_id}' not found or already acknowledged"
            )
        return {"status": "acknowledged", "alert_id": alert_id}
    finally:
        conn.close()
