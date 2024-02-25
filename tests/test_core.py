import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from typed_contracts import (
    Contract,
    ContractViolationError,
    FieldSpec,
    SchemaMismatchError,
    email_spec,
    slug_spec,
)


def user_contract() -> Contract:
    return Contract(
        [
            FieldSpec("id", int, min_value=1),
            email_spec(),
            FieldSpec("role", str, choices=("admin", "user")),
        ]
    )


def test_valid_payload_passes():
    result = user_contract().validate({"id": 7, "email": "a@b.io", "role": "user"})
    assert result.ok
    assert result.value == {"id": 7, "email": "a@b.io", "role": "user"}


def test_missing_required_reports_violation():
    result = user_contract().validate({})
    assert not result.ok
    assert any("required" in str(v) for v in result.violations)


def test_type_mismatch_detected():
    result = user_contract().validate({"id": "seven", "email": "a@b.io", "role": "user"})
    assert any(isinstance(v, SchemaMismatchError) for v in result.violations)


def test_bool_rejected_for_numeric():
    result = user_contract().validate({"id": True, "email": "a@b.io", "role": "user"})
    assert not result.ok


def test_range_bounds_enforced():
    contract = Contract([FieldSpec("age", int, min_value=18, max_value=120)])
    assert contract.validate({"age": 30}).ok
    assert not contract.validate({"age": 5}).ok
    assert not contract.validate({"age": 200}).ok


def test_length_bounds_enforced():
    contract = Contract([FieldSpec("name", str, min_length=2, max_length=10)])
    assert contract.validate({"name": "ali"}).ok
    assert not contract.validate({"name": "a"}).ok
    assert not contract.validate({"name": "x" * 11}).ok


def test_choices_reject_unknown():
    result = user_contract().validate({"id": 1, "email": "x@y.z", "role": "ghost"})
    assert any("not in" in str(v) for v in result.violations)


def test_email_pattern():
    contract = Contract([email_spec()])
    assert contract.validate({"email": "good@mail.com"}).ok
    assert not contract.validate({"email": "bad-mail"}).ok


def test_slug_pattern_allows_hyphen_not_leading():
    contract = Contract([slug_spec()])
    assert contract.validate({"slug": "my-post-2"}).ok
    assert not contract.validate({"slug": "-bad"}).ok


def test_strict_extra_flags_unknown_fields():
    contract = Contract([FieldSpec("a", int)], strict_extra=True)
    result = contract.validate({"a": 1, "ghost": True})
    assert not result.ok
    assert any("unexpected field: 'ghost'" in str(v) for v in result.violations)


def test_lenient_extra_ignored_by_default():
    contract = Contract([FieldSpec("a", int)])
    assert contract.validate({"a": 1, "noise": "ok"}).ok


def test_raise_if_invalid_raises_with_summary():
    contract = Contract([FieldSpec("n", int)])
    with pytest.raises(ContractViolationError):
        contract.validate({"n": "text"}).raise_if_invalid()


def test_duplicate_field_names_rejected():
    with pytest.raises(ContractViolationError):
        Contract([FieldSpec("x", int), FieldSpec("x", str)])


def test_optional_field_none_passes():
    contract = Contract([FieldSpec("note", str, required=False)])
    assert contract.validate({"note": None}).ok
