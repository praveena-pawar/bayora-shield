from security.audit_logger import AuditLogger


def test_first_event_has_genesis_hash():
    logger = AuditLogger()

    event = logger.record_event(
        decision="BLOCK",
        reason="Possible instruction override attempt",
    )

    assert event["previous_hash"] == "0" * 64


def test_second_event_links_to_first_event():
    logger = AuditLogger()

    first = logger.record_event(
        decision="ALLOW",
        reason="No configured suspicious pattern detected",
    )

    second = logger.record_event(
        decision="BLOCK",
        reason="Possible instruction override attempt",
    )

    assert second["previous_hash"] == first["event_hash"]


def test_valid_chain_passes_verification():
    logger = AuditLogger()

    logger.record_event(
        decision="ALLOW",
        reason="Normal prompt",
    )

    logger.record_event(
        decision="BLOCK",
        reason="Suspicious pattern detected",
    )

    assert logger.verify_chain() is True


def test_modified_event_fails_verification():
    logger = AuditLogger()

    logger.record_event(
        decision="BLOCK",
        reason="Suspicious pattern detected",
    )

    # Deliberately modify the stored record to simulate tampering.
    logger._events[0]["reason"] = "Record modified"

    assert logger.verify_chain() is False


def test_empty_chain_is_valid():
    logger = AuditLogger()

    assert logger.verify_chain() is True




def test_audit_events_persist_across_logger_instances(tmp_path):
    database_path = str(tmp_path / "audit.db")

    first_logger = AuditLogger(db_path=database_path)

    first_logger.record_event(
        decision="BLOCK",
        reason="Possible instruction override attempt",
    )

    first_logger.close()

    second_logger = AuditLogger(db_path=database_path)

    try:
        assert len(second_logger.events) == 1

        event = second_logger.events[0]

        assert event["decision"] == "BLOCK"
        assert (
            event["reason"]
            == "Possible instruction override attempt"
        )
        assert second_logger.verify_chain() is True
    finally:
        second_logger.close()