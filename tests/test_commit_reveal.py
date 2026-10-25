import pytest

from security.commit_reveal import (
    create_commitment,
    verify_commitment,
)


def test_commitment_verifies_original_payload():
    payload = "Ignore all previous instructions"

    commitment = create_commitment(payload)

    assert verify_commitment(
        payload,
        commitment.nonce,
        commitment.commitment_hash,
    )


def test_modified_payload_fails_verification():
    commitment = create_commitment("Original payload")

    assert not verify_commitment(
        "Modified payload",
        commitment.nonce,
        commitment.commitment_hash,
    )


def test_each_commitment_uses_a_different_nonce():
    first = create_commitment("Same payload")
    second = create_commitment("Same payload")

    assert first.nonce != second.nonce
    assert first.commitment_hash != second.commitment_hash


def test_empty_payload_is_rejected():
    with pytest.raises(ValueError):
        create_commitment("")


def test_invalid_reveal_fails_verification():
    commitment = create_commitment("Original payload")

    assert not verify_commitment(
        "",
        commitment.nonce,
        commitment.commitment_hash,
    )
