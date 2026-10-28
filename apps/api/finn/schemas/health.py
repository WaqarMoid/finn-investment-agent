from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status: ok or degraded")
    version: str = Field(..., description="Application version")
    timestamp_utc: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Current UTC timestamp"
    )
    mode: str = Field(default="live", description="System operational mode: live or replay")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Component readiness details")
