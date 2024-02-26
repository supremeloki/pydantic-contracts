# typed-contracts

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Declarative data contracts that return every violation at once — types, ranges, lengths, patterns, choices — with frozen results and a strict mode that rejects unknown fields.

## 🚀 Overview

Boundary data lies: IDs arrive as strings, ages as `True`, roles nobody defined. `typed-contracts` describes what valid input looks like as plain `FieldSpec` objects, validates in one pass, and returns a frozen `ContractResult` carrying *all* violations — so callers fix everything in a round-trip, not one error per attempt. No metaclass magic, no import-time surprises; contracts are just values you can compose, store, and test.

## ✨ Features

- **Typed violation hierarchy:** `SchemaMismatchError` / `RangeViolationError` / `FormatViolationError` under one base — catch broadly or precisely
- **Collect-all reporting:** every field's problems returned together
- **Numeric + length bounds:** `min_value/max_value`, `min_length/max_length`
- **Pattern & choice rules:** compiled regex patterns, literal choice tuples
- **Strict mode:** unknown keys become violations instead of silent pass-through
- **Bool-guard:** `True` never sneaks through as an integer
- **Helper factories:** `email_spec()`, `slug_spec()` with sane defaults
- **Zero dependencies**

## 🚧 Structure

```
pydantic-contracts/
├── src/typed_contracts/
│   ├── __init__.py
│   └── core.py
├── tests/
│   └── test_core.py
├── README.md
└── pyproject.toml
```

## 📦 Installation

```bash
git clone https://github.com/supremeloki/pydantic-contracts.git
cd pydantic-contracts
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## 📋 Requirements

- Python 3.11+
- No runtime dependencies

## 🏃 Quick Start

```python
from typed_contracts import Contract, FieldSpec, email_spec

user_contract = Contract(
    [
        FieldSpec("id", int, min_value=1),
        FieldSpec("role", str, choices=("admin", "user")),
        email_spec(),
    ],
    strict_extra=True,
)

result = user_contract.validate({"id": 7, "email": "a@b.io", "role": "user"})
if result.ok:
    print(result.value)
else:
    for v in result.violations:
        print(v)
```

### Raise on first use

```python
clean = user_contract.validate(payload).raise_if_invalid()
```

## 🔧 Error Handling

```text
ContractViolationError
├── SchemaMismatchError     # type/choice/required failures
├── RangeViolationError     # numeric or length bounds
└── FormatViolationError    # regex pattern mismatch
```

## 🧪 Testing

```bash
pytest tests/ -v
```

## 📝 Code Quality

- Full type hints (`X | None` style)
- Zero comments — names carry the meaning
- Generic `ContractResult[T]`, frozen dataclasses throughout

## 📄 License

MIT — see [LICENSE](LICENSE).

## 👤 Author

**Kooroush Masoumi**

---

⭐ Star this repo if you find it useful!
