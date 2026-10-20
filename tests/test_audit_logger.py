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