import json
import uuid
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

class JobManager:
    """Durable SQLite-backed background job queue with atomic lease claims,

    heartbeats, bounded retries, and automatic crash recovery.
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def enqueue_job(
        self,
        job_type: str,
        dedup_key: str,
        company_id: Optional[str] = None,
        session_id: Optional[str] = None,
        progress_detail: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        now_utc = datetime.now(timezone.utc).isoformat()
        job_id = f"job-{uuid.uuid4()}"
        detail_json = json.dumps(progress_detail or {})

        # Insert or ignore duplicate active jobs
        self.conn.execute("""
            INSERT OR IGNORE INTO jobs (
                id, job_type, dedup_key, session_id, company_id,
                status, stage, attempt_count, progress_detail_json,
                created_at_utc, updated_at_utc
            ) VALUES (?, ?, ?, ?, ?, 'queued', 'enqueued', 0, ?, ?, ?)
        """, (
            job_id, job_type, dedup_key, session_id, company_id,
            detail_json, now_utc, now_utc
        ))
        self.conn.commit()

        # Fetch existing or newly created job by dedup_key
        row = self.conn.execute(
            "SELECT * FROM jobs WHERE dedup_key = ?", (dedup_key,)
        ).fetchone()
        return dict(row)

    def claim_job(self, lease_seconds: int = 30) -> Optional[Dict[str, Any]]:
        """Atomically claims the next queued or expired running job."""
        now = datetime.now(timezone.utc)
        now_utc = now.isoformat()
        lease_until = (now + timedelta(seconds=lease_seconds)).isoformat()

        cursor = self.conn.cursor()
        cursor.execute("BEGIN IMMEDIATE;")
        try:
            # Find eligible job: queued or running with expired lease
            row = cursor.execute("""
                SELECT id, attempt_count FROM jobs
                WHERE status = 'queued'
                   OR (status = 'running' AND lease_until_utc < ?)
                ORDER BY created_at_utc ASC
                LIMIT 1
            """, (now_utc,)).fetchone()

            if not row:
                cursor.execute("COMMIT;")
                return None

            job_id = row["id"]
            new_attempts = row["attempt_count"] + 1

            cursor.execute("""
                UPDATE jobs SET
                    status = 'running',
                    stage = 'executing',
                    attempt_count = ?,
                    lease_until_utc = ?,
                    heartbeat_utc = ?,
                    updated_at_utc = ?
                WHERE id = ?
            """, (new_attempts, lease_until, now_utc, now_utc, job_id))

            cursor.execute("COMMIT;")
            claimed = self.conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            return dict(claimed)
        except Exception:
            cursor.execute("ROLLBACK;")
            raise

    def heartbeat_job(self, job_id: str, lease_seconds: int = 30) -> bool:
        now = datetime.now(timezone.utc)
        now_utc = now.isoformat()
        lease_until = (now + timedelta(seconds=lease_seconds)).isoformat()

        cursor = self.conn.execute("""
            UPDATE jobs SET
                heartbeat_utc = ?,
                lease_until_utc = ?,
                updated_at_utc = ?
            WHERE id = ? AND status = 'running'
        """, (now_utc, lease_until, now_utc, job_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def complete_job(self, job_id: str, output_id: Optional[str] = None) -> bool:
        now_utc = datetime.now(timezone.utc).isoformat()
        cursor = self.conn.execute("""
            UPDATE jobs SET
                status = 'succeeded',
                stage = 'completed',
                output_id = ?,
                updated_at_utc = ?
            WHERE id = ?
        """, (output_id, now_utc, job_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def fail_job(self, job_id: str, error_message: str, max_attempts: int = 3) -> bool:
        now_utc = datetime.now(timezone.utc).isoformat()
        row = self.conn.execute("SELECT attempt_count FROM jobs WHERE id = ?", (job_id,)).fetchone()
        attempts = row["attempt_count"] if row else 1

        if attempts >= max_attempts:
            new_status = "failed"
            new_stage = "exhausted_retries"
        else:
            new_status = "queued"  # Requeue for retry
            new_stage = f"retry_pending_attempt_{attempts}"

        cursor = self.conn.execute("""
            UPDATE jobs SET
                status = ?,
                stage = ?,
                error_message = ?,
                lease_until_utc = NULL,
                updated_at_utc = ?
            WHERE id = ?
        """, (new_status, new_stage, error_message, now_utc, job_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def recover_stale_jobs(self) -> int:
        """Finds any running jobs whose lease expired (worker crash recovery) and resets them to queued."""
        now_utc = datetime.now(timezone.utc).isoformat()
        cursor = self.conn.execute("""
            UPDATE jobs SET
                status = 'queued',
                stage = 'recovered_from_stale_lease',
                lease_until_utc = NULL,
                updated_at_utc = ?
            WHERE status = 'running' AND lease_until_utc <= ?
        """, (now_utc, now_utc))
        self.conn.commit()
        return cursor.rowcount
