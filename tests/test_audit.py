from __future__ import annotations

import json


def test_audit_event_is_jsonl_and_does_not_require_pii(tmp_path, monkeypatch) -> None:
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("AUDIT_LOG_PATH", str(audit_path))

    import app.audit as audit

    monkeypatch.setattr(audit, "AUDIT_LOG_PATH", audit_path)
    audit.write_audit_event("incident_enabled", incident="cost_spike", state=True)

    record = json.loads(audit_path.read_text(encoding="utf-8"))
    assert record["event"] == "incident_enabled"
    assert record["incident"] == "cost_spike"
    assert record["state"] is True
