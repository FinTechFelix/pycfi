# pycfi

A Python package for reading **CFI codes** based on the ISO 10962 standard. Turns 6-character CFI codes into structured, human-readable descriptions of financial instruments.

---

## What is a CFI Code?

A **CFI (Classification of Financial Instruments)** code is a 6-character identifier used to classify financial instruments globally.

| Position | Meaning | Example |
|---|---|---|
| 1 | Category (e.g. Equity, Debt) | `E` → Equity |
| 2 | Group (e.g. Common Shares, Bonds) | `S` → Common/Ordinary Shares |
| 3–6 | Attributes specific to the instrument type | Voting rights, payment status, form, etc. |

---

## Installation

```bash
pip install pycfi
```

---

## Quick Start

```python
from pycfi import CFICode

print(CFICode("ESVUFR"))
```

Output:

```
CFICode('ESVUFR')
  Category : equity
  Group    : common/ordinary shares
  Attributes:
    voting_right   : voting
    ownership      : free
    payment_status : fully paid
    form           : registered
```

---

## Use Cases

### 1. Identify what an instrument is

```python
from pycfi import CFICode

code = CFICode("ESVUFR")
print(code.category)  # "equity"
print(code.group)     # "common/ordinary shares"
```

Works across all 14 categories defined in ISO 10962 — equities, debt instruments, listed options, futures, swaps, forwards, collective investment vehicles, and more.

---

### 2. See the full breakdown

Just print the object — category, group, and all attributes are displayed.

```python
from pycfi import CFICode

print(CFICode("RWSNCA"))
```

```
CFICode('RWSNCA')
  Category : entitlements
  Group    : warrants
  Attributes:
    underlying_assets     : equities
    type                  : naked warrants
    call_put              : call
    exercise_option_style : american
```

---

### 3. Read a specific attribute by name

```python
from pycfi import CFICode

code = CFICode("RWSNCA")
attr = code.get_attribute("underlying_assets")
print(attr.value)     # "equities"
```

Returns `None` if the attribute is not present for that instrument type.

---

### 4. Iterate over all attributes

```python
from pycfi import CFICode

code = CFICode("RWSNCA")
for attr in code.attributes:
    print(f"{attr.name}: {attr.value}")

# underlying_assets: equities
# type: naked warrants
# call_put: call
# exercise_option_style: american
```

---

### 5. Discover all valid values for each attribute position

Pass `show_options=True` to see every valid value an attribute position can hold — useful for building UIs, dropdowns, or validation logic.

```python
from pycfi import CFICode

code = CFICode("ESVUFR", show_options=True)
for attr in code.attributes:
    print(f"{attr.name}: {attr.value}  (options: {attr.options})")

# voting_right: voting  (options: ['voting', 'non-voting', 'restricted', 'enhanced voting'])
# ownership: free  (options: ['restrictions', 'free'])
# payment_status: fully paid  (options: ['fully paid', 'nil paid', 'partly paid'])
# form: registered  (options: ['bearer', 'registered', 'bearer/registered', 'others'])
```

---

### 6. Filter or classify a list of instruments

```python
from pycfi import CFICode

cfi_codes = ["ESVUFR", "RWSNCA", "OPASPS", "DBFUBB", "FFCPSX"]

equities = [c for c in cfi_codes if CFICode(c).category == "equity"]
options  = [c for c in cfi_codes if CFICode(c).category == "listed options"]

print(equities)  # ["ESVUFR"]
print(options)   # ["OPASPS"]
```

---

### 7. Enrich financial data

Add human-readable fields to a record or DataFrame row.

```python
from pycfi import CFICode

def enrich(record: dict) -> dict:
    code = CFICode(record["cfi"])
    voting = code.get_attribute("voting_right")
    return {
        **record,
        "category": code.category,
        "group": code.group,
        "voting_right": voting.value if voting else None,
    }

instrument = {"isin": "US0378331005", "cfi": "ESVUFR"}
print(enrich(instrument))
# {"isin": "US0378331005", "cfi": "ESVUFR", "category": "equity",
#  "group": "common/ordinary shares", "voting_right": "voting"}
```

---

### 8. Handle unknown or partially defined codes

Unrecognised characters return `None` rather than raising an error. You can safely handle unknown codes in production pipelines.

```python
from pycfi import CFICode

code = CFICode("ZZZZZZ")
print(code.category)    # None
print(code.group)       # None
print(code.attributes)  # raw characters with name=None
```

---

### 9. Validate a CFI code format

`pycfi` raises a `ValueError` for structurally invalid inputs — wrong type or wrong length.

```python
from pycfi import CFICode

def is_valid(cfi: str) -> bool:
    try:
        CFICode(cfi)
        return True
    except ValueError:
        return False

print(is_valid("ESVUFR"))  # True
print(is_valid("ES"))      # False — wrong length
print(is_valid(None))      # False — wrong type
```

---

## API Reference

### `CFICode(code, show_options=False)`

The only class you need. Instantiate with a 6-character CFI code string.

| Attribute | Type | Description |
|---|---|---|
| `raw` | `str` | The uppercased input code |
| `category` | `str \| None` | Category name (lowercase) |
| `group` | `str \| None` | Group name (lowercase) |
| `attributes` | `list[CFIAttribute]` | Attribute list (excludes N/A positions) |

**Methods:**

- `get_attribute(name: str) -> CFIAttribute | None` — Look up an attribute by name.
- `print(code)` — Displays the full human-readable breakdown.
- `repr(code)` — One-line summary: `CFICode('ESVUFR', category='equity', group='common/ordinary shares')`

### `CFIAttribute`

| Field | Type | Description |
|---|---|---|
| `position` | `int` | Character position in the code (3-6) |
| `name` | `str \| None` | Attribute name (e.g. `"voting_right"`) |
| `value` | `str \| None` | Decoded value (e.g. `"voting"`) |
| `options` | `list[str]` | All valid values (populated when `show_options=True`) |

---

## Supported Categories

| Code | Category |
|---|---|
| E | Equity |
| C | Collective investment vehicles |
| D | Debt instruments |
| R | Entitlements (rights, warrants) |
| O | Listed options |
| F | Futures |
| S | Swaps |
| H | Non-listed and complex listed options |
| I | Spot |
| J | Forwards |
| K | Strategies |
| L | Financing |
| T | Reference instruments |
| M | Others |

---

## License

MIT
