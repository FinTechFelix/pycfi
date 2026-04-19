# CFI Code Decoder DX Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve developer experience by replacing the generic `Decoder` class and plain dict returns with typed dataclasses, a `CFICode` object-oriented interface, a module-level `decode()` function, and fixing several small bugs.

**Architecture:** Introduce a `CFIAttribute` dataclass and a `CFICode` class whose `__init__` performs decoding directly. Keep a `CFIDecoder` class as a thin wrapper for users who prefer the decoder pattern. Add a module-level `decode()` convenience function. Filter out `na_X` placeholder attributes from decoded output. Fix the validation order bug.

**Tech Stack:** Python 3.9+, `dataclasses` (stdlib), `__future__.annotations` for modern type hint syntax on 3.9.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `src/cfi_code_decoder/decoder.py` | Rewrite | `CFIAttribute`, `CFICode`, `CFIDecoder`, `decode()` |
| `src/cfi_code_decoder/__init__.py` | Update | Re-export all public symbols |
| `pyproject.toml` | Update | Fix name from `cfi-code-parser` → `cfi-code-decoder` |
| `src/cfi_code_decoder/map.py` | No change | Lookup tables (untouched) |

---

### Task 1: Fix `pyproject.toml` package name

**Files:**
- Modify: `pyproject.toml:6`

- [ ] **Step 1: Update the package name**

Change line 6 of `pyproject.toml` from:
```toml
name = "cfi-code-parser"
```
to:
```toml
name = "cfi-code-decoder"
```

- [ ] **Step 2: Verify**

```bash
grep '^name' pyproject.toml
```
Expected output: `name = "cfi-code-decoder"`

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "fix: align pyproject.toml package name with repository name"
```

---

### Task 2: Rewrite `decoder.py` with typed classes and convenience function

**Files:**
- Rewrite: `src/cfi_code_decoder/decoder.py`

- [ ] **Step 1: Replace the entire file contents**

```python
from __future__ import annotations

from dataclasses import dataclass, field

from .map import ATTRIBUTE_MAP, CATEGORY_MAP, GROUP_MAP


@dataclass
class CFIAttribute:
    """A single decoded attribute from positions 3–6 of a CFI code."""

    position: int
    name: str | None
    value: str | None
    options: list[str] = field(default_factory=list)


class CFICode:
    """Decodes an ISO 10962 CFI code into its category, group, and attributes.

    Instantiate with a 6-character CFI code string. Decoded fields are
    available directly on the instance.

    Example::

        code = CFICode("RWSNCA")
        code.category          # "entitlements"
        code.group             # "warrants"
        code.get_attribute("underlying_assets").value  # "equities"
    """

    def __init__(self, code: str, show_options: bool = False) -> None:
        if not isinstance(code, str):
            raise ValueError("CFI code must be of type str.")
        code = code.upper()
        if len(code) != 6:
            raise ValueError("CFI code must be exactly 6 characters long.")

        self.raw: str = code

        category_letter = code[0]
        group_letter = code[1]

        category = CATEGORY_MAP.get(category_letter)
        self.category: str | None = category.lower() if category else None

        group = GROUP_MAP.get(category_letter, {}).get(group_letter)
        self.group: str | None = group.lower() if group else None

        self.attributes: list[CFIAttribute] = []
        mapping_key = (category_letter, group_letter)

        if mapping_key in ATTRIBUTE_MAP:
            for idx, attr_info in enumerate(ATTRIBUTE_MAP[mapping_key]):
                name = attr_info.get("name")
                # Skip not-applicable placeholder positions
                if name and name.startswith("na_"):
                    continue
                raw_char = code[2 + idx]
                attr_value = attr_info["mapping"].get(raw_char)
                options = (
                    [v.lower() for v in attr_info["mapping"].values()]
                    if show_options
                    else []
                )
                self.attributes.append(
                    CFIAttribute(
                        position=idx + 3,
                        name=name,
                        value=attr_value.lower() if attr_value else None,
                        options=options,
                    )
                )
        else:
            for i in range(4):
                self.attributes.append(
                    CFIAttribute(
                        position=i + 3,
                        name=None,
                        value=code[2 + i].lower(),
                    )
                )

    def get_attribute(self, name: str) -> CFIAttribute | None:
        """Return the attribute with the given name, or None if not present."""
        return next((a for a in self.attributes if a.name == name), None)

    def __repr__(self) -> str:
        return (
            f"CFICode({self.raw!r}, "
            f"category={self.category!r}, "
            f"group={self.group!r})"
        )

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CFICode):
            return self.raw == other.raw
        return NotImplemented


class CFIDecoder:
    """Stateless decoder that returns a CFICode for each call to decode()."""

    def decode(self, cfi_code: str, show_options: bool = False) -> CFICode:
        return CFICode(cfi_code, show_options)


def decode(cfi_code: str, show_options: bool = False) -> CFICode:
    """Decode an ISO 10962 CFI code.

    Convenience wrapper — equivalent to ``CFICode(cfi_code, show_options)``.
    """
    return CFICode(cfi_code, show_options)


if __name__ == "__main__":
    print(decode("RWSNCA"))
    print(decode("RWSNCA").get_attribute("underlying_assets"))
```

- [ ] **Step 2: Quick smoke test in the terminal**

```bash
cd /Users/felix.dahlmeyer/Documents/GitHub/cfi-code-decoder
python -m src.cfi_code_decoder.decoder
```

Expected output (two lines):
```
CFICode('RWSNCA', category='entitlements', group='warrants')
CFIAttribute(position=3, name='underlying_assets', value='equities', options=[])
```

- [ ] **Step 3: Commit**

```bash
git add src/cfi_code_decoder/decoder.py
git commit -m "feat: replace Decoder with CFICode, CFIDecoder, CFIAttribute, and decode()"
```

---

### Task 3: Update `__init__.py` to export all public symbols

**Files:**
- Modify: `src/cfi_code_decoder/__init__.py`

- [ ] **Step 1: Replace the file contents**

```python
from .decoder import CFIAttribute, CFICode, CFIDecoder, decode
```

- [ ] **Step 2: Verify the public API**

```bash
python -c "
from cfi_code_decoder import CFICode, CFIDecoder, CFIAttribute, decode
r = decode('ESVRFB')
print(r)
print(r.attributes)
print(r.get_attribute('voting_right'))
"
```

Expected output:
```
CFICode('ESVRFB', category='equity', group='common/ordinary shares')
[CFIAttribute(position=3, name='voting_right', value='voting', options=[]), CFIAttribute(position=4, name='ownership', value='restrictions', options=[]), CFIAttribute(position=5, name='payment_status', value='fully paid', options=[]), CFIAttribute(position=6, name='form', value='bearer', options=[])]
CFIAttribute(position=3, name='voting_right', value='voting', options=[])
```

- [ ] **Step 3: Commit**

```bash
git add src/cfi_code_decoder/__init__.py
git commit -m "chore: export CFICode, CFIDecoder, CFIAttribute, and decode from package root"
```

---

### Task 4: Write tests to lock in the behaviour

**Files:**
- Create: `tests/test_decoder.py`

- [ ] **Step 1: Create the test file**

```python
import pytest
from cfi_code_decoder import CFIAttribute, CFICode, CFIDecoder, decode


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_rejects_non_string():
    with pytest.raises(ValueError, match="type str"):
        CFICode(123)  # type: ignore[arg-type]


def test_rejects_wrong_length():
    with pytest.raises(ValueError, match="6 characters"):
        CFICode("ES")


def test_type_check_before_length_check():
    # Non-string should raise the type error, not crash on len()
    with pytest.raises(ValueError, match="type str"):
        CFICode(None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Category and group decoding
# ---------------------------------------------------------------------------

def test_known_category_and_group():
    code = CFICode("ESVTFB")
    assert code.category == "equity"
    assert code.group == "common/ordinary shares"


def test_unknown_category_returns_none():
    code = CFICode("ZZZZZZ")
    assert code.category is None
    assert code.group is None


def test_raw_is_uppercased():
    code = CFICode("esvtfb")
    assert code.raw == "ESVTFB"


# ---------------------------------------------------------------------------
# Attribute decoding
# ---------------------------------------------------------------------------

def test_attributes_are_cfiattribute_instances():
    code = CFICode("ESVTFB")
    assert all(isinstance(a, CFIAttribute) for a in code.attributes)


def test_known_attribute_value():
    code = CFICode("ESVTFB")
    attr = code.get_attribute("voting_right")
    assert attr is not None
    assert attr.value == "voting"


def test_get_attribute_returns_none_for_unknown_name():
    code = CFICode("ESVTFB")
    assert code.get_attribute("nonexistent") is None


def test_na_attributes_are_filtered_out():
    # Group EM has na_1, na_2, na_3 — only "form" should survive
    code = CFICode("EMXXXB")
    names = [a.name for a in code.attributes]
    assert not any(n and n.startswith("na_") for n in names)
    assert "form" in names


def test_attribute_position_is_correct():
    code = CFICode("ESVTFB")
    voting = code.get_attribute("voting_right")
    assert voting.position == 3  # first attribute char is at position 3


# ---------------------------------------------------------------------------
# show_options
# ---------------------------------------------------------------------------

def test_options_empty_by_default():
    code = CFICode("ESVTFB")
    for attr in code.attributes:
        assert attr.options == []


def test_options_populated_with_show_options():
    code = CFICode("ESVTFB", show_options=True)
    voting = code.get_attribute("voting_right")
    assert "voting" in voting.options
    assert "non-voting" in voting.options


# ---------------------------------------------------------------------------
# CFIDecoder wrapper
# ---------------------------------------------------------------------------

def test_cfidecoder_returns_cficode():
    decoder = CFIDecoder()
    result = decoder.decode("RWSNCA")
    assert isinstance(result, CFICode)
    assert result.category == "entitlements"


# ---------------------------------------------------------------------------
# Module-level decode() function
# ---------------------------------------------------------------------------

def test_decode_function_returns_cficode():
    result = decode("RWSNCA")
    assert isinstance(result, CFICode)


def test_decode_function_matches_cficode_directly():
    assert decode("RWSNCA") == CFICode("RWSNCA")


# ---------------------------------------------------------------------------
# Repr and equality
# ---------------------------------------------------------------------------

def test_repr_contains_raw_category_group():
    code = CFICode("ESVTFB")
    r = repr(code)
    assert "ESVTFB" in r
    assert "equity" in r
    assert "common/ordinary shares" in r


def test_equality_same_code():
    assert CFICode("ESVTFB") == CFICode("ESVTFB")


def test_equality_case_insensitive_input():
    assert CFICode("esvtfb") == CFICode("ESVTFB")


def test_inequality_different_codes():
    assert CFICode("ESVTFB") != CFICode("RWSNCA")
```

- [ ] **Step 2: Install the package in editable mode if not already done**

```bash
pip install -e .
```

- [ ] **Step 3: Run the tests**

```bash
pytest tests/test_decoder.py -v
```

Expected: all tests PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/test_decoder.py
git commit -m "test: add full test suite covering CFICode, CFIDecoder, decode(), and CFIAttribute"
```

---

## Self-Review

### Spec coverage

| Requirement | Covered by |
|---|---|
| Fix `pyproject.toml` name inconsistency | Task 1 |
| Rename `Decoder` → `CFIDecoder` | Task 2 |
| Add `CFICode` object-oriented interface | Task 2 |
| Return `CFIAttribute` dataclass instead of dicts | Task 2 |
| Add `get_attribute(name)` lookup | Task 2 |
| Add module-level `decode()` | Task 2 |
| Filter `na_X` placeholder attributes | Task 2 |
| Fix validation order (type check before length check) | Task 2 |
| Export all public symbols | Task 3 |
| Tests for all new behaviour | Task 4 |

### Placeholder scan

No TBDs, no "similar to Task N" patterns, no steps without code.

### Type consistency

- `CFIAttribute` defined in Task 2, referenced in Task 4 tests — consistent.
- `get_attribute()` returns `CFIAttribute | None` — tests use `.value` on the result, which matches the dataclass field name.
- `decode()` returns `CFICode` — tests assert `isinstance(result, CFICode)` ✓
