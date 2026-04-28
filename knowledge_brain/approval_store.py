from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS approvals (
    session_id TEXT NOT NULL,
    action_hash TEXT NOT NULL,
    namespace TEXT NOT NULL,
    capability TEXT NOT NULL,
    requested_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    approved_at TEXT,
    denied_at TEXT,
    invalidated_at TEXT,
    final_status TEXT NOT NULL CHECK(final_status IN ('PENDING', 'APPROVED', 'DENIED', 'EXPIRED')),
    reason TEXT NOT NULL DEFAULT '',
    approver_meta_json TEXT NOT NULL DEFAULT '{}',
    PRIMARY KEY (session_id, action_hash)
);
"""


@dataclass(slots=True)
class ApprovalProjection:
    session_id: str
    action_hash: str
    namespace: str
    capability: str
    requested_at: str
    expires_at: str
    final_status: str
    approved_at: str | None = None
    denied_at: str | None = None
    invalidated_at: str | None = None
    reason: str = ""
    approver_meta_json: str = "{}"


class ApprovalStore:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)

    def init_schema(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(SCHEMA)

    def upsert_projection(self, projection: ApprovalProjection) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO approvals (
                    session_id, action_hash, namespace, capability, requested_at, expires_at,
                    approved_at, denied_at, invalidated_at, final_status, reason, approver_meta_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    projection.session_id,
                    projection.action_hash,
                    projection.namespace,
                    projection.capability,
                    projection.requested_at,
                    projection.expires_at,
                    projection.approved_at,
                    projection.denied_at,
                    projection.invalidated_at,
                    projection.final_status,
                    projection.reason,
                    projection.approver_meta_json,
                ),
            )

    def get_projection(self, session_id: str, action_hash: str) -> ApprovalProjection | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT session_id, action_hash, namespace, capability, requested_at, expires_at,
                       approved_at, denied_at, invalidated_at, final_status, reason, approver_meta_json
                FROM approvals
                WHERE session_id = ? AND action_hash = ?
                """,
                (session_id, action_hash),
            ).fetchone()
        if row is None:
            return None
        return ApprovalProjection(
            session_id=row[0],
            action_hash=row[1],
            namespace=row[2],
            capability=row[3],
            requested_at=row[4],
            expires_at=row[5],
            approved_at=row[6],
            denied_at=row[7],
            invalidated_at=row[8],
            final_status=row[9],
            reason=row[10],
            approver_meta_json=row[11],
        )

    def list_recent(
        self,
        *,
        namespace: str | None = None,
        session_id: str | None = None,
        limit: int = 5,
    ) -> list[ApprovalProjection]:
        where: list[str] = []
        params: list[str | int] = []
        if namespace is not None:
            where.append("namespace = ?")
            params.append(namespace)
        if session_id is not None:
            where.append("session_id = ?")
            params.append(session_id)
        clause = f" WHERE {' AND '.join(where)}" if where else ""
        query = (
            "SELECT session_id, action_hash, namespace, capability, requested_at, expires_at, "
            "approved_at, denied_at, invalidated_at, final_status, reason, approver_meta_json "
            f"FROM approvals{clause} ORDER BY requested_at DESC LIMIT ?"
        )
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(query, [*params, limit]).fetchall()
        return [
            ApprovalProjection(
                session_id=row[0],
                action_hash=row[1],
                namespace=row[2],
                capability=row[3],
                requested_at=row[4],
                expires_at=row[5],
                approved_at=row[6],
                denied_at=row[7],
                invalidated_at=row[8],
                final_status=row[9],
                reason=row[10],
                approver_meta_json=row[11],
            )
            for row in rows
        ]
