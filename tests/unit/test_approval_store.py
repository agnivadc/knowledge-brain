from pathlib import Path

from knowledge_brain.approval_store import ApprovalProjection, ApprovalStore


def test_upsert_marks_expired_projection(tmp_path: Path) -> None:
    db_path = tmp_path / "knowledge.db"
    store = ApprovalStore(db_path)
    store.init_schema()

    store.upsert_projection(
        ApprovalProjection(
            session_id="sess-123",
            action_hash="hash-1",
            namespace="brain-playground",
            capability="trade_execute",
            requested_at="2026-04-27T10:00:00+00:00",
            expires_at="2026-04-27T10:00:05+00:00",
            invalidated_at="2026-04-27T10:00:06+00:00",
            final_status="EXPIRED",
            reason="expired",
        )
    )

    projection = store.get_projection("sess-123", "hash-1")

    assert projection is not None
    assert projection.final_status == "EXPIRED"
