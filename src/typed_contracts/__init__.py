from .core import (
    Contract,
    ContractResult,
    ContractViolationError,
    FieldSpec,
    FormatViolationError,
    RangeViolationError,
    SchemaMismatchError,
    email_spec,
    slug_spec,
)

__all__ = [
    "Contract",
    "ContractResult",
    "ContractViolationError",
    "FieldSpec",
    "FormatViolationError",
    "RangeViolationError",
    "SchemaMismatchError",
    "email_spec",
    "slug_spec",
]

__version__ = "0.1.0"
