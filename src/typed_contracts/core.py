from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class ContractViolationError(Exception):
    pass


class SchemaMismatchError(ContractViolationError):
    pass


class RangeViolationError(ContractViolationError):
    pass


class FormatViolationError(ContractViolationError):
    pass


EMAIL_PATTERN: re.Pattern[str] = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
SLUG_PATTERN: re.Pattern[str] = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


@dataclass(frozen=True)
class FieldSpec:
    name: str
    expected_type: type
    required: bool = True
    min_value: int | float | None = None
    max_value: int | float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: re.Pattern[str] | None = None
    choices: tuple[Any, ...] = ()

    def check(self, value: Any) -> list[ContractViolationError]:
        violations: list[ContractViolationError] = []
        if value is None:
            if self.required:
                violations.append(SchemaMismatchError(f"{self.name}: required but got None"))
            return violations
        if self.expected_type in (int, float) and isinstance(value, bool):
            violations.append(SchemaMismatchError(f"{self.name}: bool not accepted for numeric"))
            return violations
        if not isinstance(value, self.expected_type):
            violations.append(
                SchemaMismatchError(
                    f"{self.name}: expected {self.expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
            )
            return violations
        if isinstance(value, (int, float)):
            if self.min_value is not None and value < self.min_value:
                violations.append(RangeViolationError(f"{self.name}: {value} < min {self.min_value}"))
            if self.max_value is not None and value > self.max_value:
                violations.append(RangeViolationError(f"{self.name}: {value} > max {self.max_value}"))
        if isinstance(value, str):
            if self.min_length is not None and len(value) < self.min_length:
                violations.append(RangeViolationError(f"{self.name}: length < {self.min_length}"))
            if self.max_length is not None and len(value) > self.max_length:
                violations.append(RangeViolationError(f"{self.name}: length > {self.max_length}"))
            if self.pattern is not None and not self.pattern.fullmatch(value):
                violations.append(FormatViolationError(f"{self.name}: pattern mismatch"))
        if self.choices and value not in self.choices:
            violations.append(
                SchemaMismatchError(f"{self.name}: {value!r} not in {self.choices}")
            )
        return violations


@dataclass(frozen=True)
class ContractResult(Generic[T]):
    ok: bool
    value: T | None = None
    violations: tuple[ContractViolationError, ...] = ()

    def raise_if_invalid(self) -> T:
        if self.ok:
            assert self.value is not None
            return self.value
        summary = "; ".join(str(v) for v in self.violations[:3])
        raise ContractViolationError(f"contract failed ({len(self.violations)}): {summary}")


class Contract:
    def __init__(self, specs: list[FieldSpec], strict_extra: bool = False) -> None:
        known = {spec.name for spec in specs}
        if len(known) != len(specs):
            raise ContractViolationError("duplicate field names in contract")
        self._specs = specs
        self._strict_extra = strict_extra

    @property
    def field_names(self) -> set[str]:
        return {spec.name for spec in self._specs}

    def validate(self, data: dict[str, Any]) -> ContractResult[dict[str, Any]]:
        violations: list[ContractViolationError] = []
        for spec in self._specs:
            violations.extend(spec.check(data.get(spec.name)))
        if self._strict_extra:
            extras = set(data) - self.field_names
            for extra in sorted(extras):
                violations.append(
                    SchemaMismatchError(f"unexpected field: {extra!r}")
                )
        if violations:
            return ContractResult(ok=False, violations=tuple(violations))
        cleaned = {k: v for k, v in data.items() if k in self.field_names or not self._strict_extra}
        return ContractResult(ok=True, value=cleaned)


def email_spec(name: str = "email", **kwargs: Any) -> FieldSpec:
    kwargs.setdefault("pattern", EMAIL_PATTERN)
    return FieldSpec(name=name, expected_type=str, **kwargs)


def slug_spec(name: str = "slug", **kwargs: Any) -> FieldSpec:
    kwargs.setdefault("pattern", SLUG_PATTERN)
    return FieldSpec(name=name, expected_type=str, **kwargs)
