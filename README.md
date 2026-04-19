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

## Use Cases

### 1. Identify what an instrument is

The most common use case — find out the category and group of any CFI code.

```python
from pycfi import decode

code = decode("ESVUFR")
print(code.category)  # "equity"
print(code.group)     # "common/ordinary shares"
```

Works across all 14 categories defined in ISO 10962 — equities, debt instruments, listed options, futures, swaps, forwards, collective investment vehicles, and more.

---

### 2. Read a specific attribute by name

Look up a named attribute without iterating through the full list.

```python
from pycfi import decode

code = decode("RWSNCA")
attr = code.get_attribute("underlying_assets")
print(attr.value)     # "equities"

attr = code.get_attribute("exercise_option_style")
print(attr.value)     # "american"
```

Returns `None` if the attribute is not present for that instrument type.

---

### 3. Inspect all attributes of an instrument

Iterate over every decoded attribute for a complete picture of the instrument.

```python
from pycfi import decode

code = decode("RWSNCA")
for attr in code.attributes:
    print(f"[{attr.position}] {attr.name}: {attr.value}")

# [3] underlying_assets: equities
# [4] type: naked warrants
# [5] call_put: call
# [6] exercise_option_style: american
```

---

### 4. Discover all valid values for each attribute position

Pass `show_options=True` to see every valid value an attribute position can hold — useful for building UIs, dropdowns, or validation logic.

```python
from pycfi import decode

code = decode("ESVUFR", show_options=True)
for attr in code.attributes:
    print(f"{attr.name}: {attr.value}  (options: {attr.options})")

# voting_right: voting  (options: ['voting', 'non-voting', 'restricted', 'enhanced voting'])
# ownership: free  (options: ['restrictions', 'free'])
# payment_status: fully paid  (options: ['fully paid', 'nil paid', 'partly paid'])
# form: registered  (options: ['bearer', 'registered', 'bearer/registered', 'others'])
```

---

### 5. Filter or classify a list of instruments

Use the decoded category and group to segment a dataset of instruments.

```python
from pycfi import decode

cfi_codes = ["ESVUFR", "RWSNCA", "OPASPS", "DBFUBB", "FFCPSX"]

equities = [c for c in cfi_codes if decode(c).category == "equity"]
options  = [c for c in cfi_codes if decode(c).category == "listed options"]

print(equities)  # ["ESVUFR"]
print(options)   # ["OPASPS"]
```

---

### 6. Enrich financial data

Add human-readable fields to a record or DataFrame row.

```python
from pycfi import decode

def enrich(record: dict) -> dict:
    code = decode(record["cfi"])
    return {
        **record,
        "category": code.category,
        "group": code.group,
        "voting_right": code.get_attribute("voting_right") and
                        code.get_attribute("voting_right").value,
    }

instrument = {"isin": "US0378331005", "cfi": "ESVUFR"}
print(enrich(instrument))
# {"isin": "US0378331005", "cfi": "ESVUFR", "category": "equity",
#  "group": "common/ordinary shares", "voting_right": "voting"}
```

---

### 7. Handle unknown or partially defined codes gracefully

Unrecognised characters return `None` rather than raising an error. You can safely handle unknown codes in production pipelines.

```python
from pycfi import decode

code = decode("ZZZZZZ")
print(code.category)    # None
print(code.group)       # None
print(code.attributes)  # raw characters with name=None
```

---

### 8. Validate a CFI code format

`pycfi` raises a `ValueError` for structurally invalid inputs — wrong type or wrong length — which you can catch in validation layers.

```python
from pycfi import decode

def is_valid(cfi: str) -> bool:
    try:
        decode(cfi)
        return True
    except ValueError:
        return False

print(is_valid("ESVUFR"))  # True
print(is_valid("ES"))      # False — wrong length
print(is_valid(None))      # False — wrong type
```

---

### 9. Use the decoder pattern (stateless, reusable)

If you prefer dependency injection or want a single decoder instance shared across your application:

```python
from pycfi import CFIDecoder

decoder = CFIDecoder()

codes = ["ESVUFR", "RWSNCA", "DBFUBB"]
for raw in codes:
    result = decoder.decode(raw)
    print(f"{raw}: {result.category} / {result.group}")
```

---

## API Reference

### `decode(cfi_code, show_options=False) → CFICode`

Module-level convenience function. Equivalent to `CFICode(cfi_code, show_options)`.

### `CFICode(code, show_options=False)`

| Attribute | Type | Description |
|---|---|---|
| `raw` | `str` | The uppercased input code |
| `category` | `str \| None` | Decoded category name (lowercase) |
| `group` | `str \| None` | Decoded group name (lowercase) |
| `attributes` | `list[CFIAttribute]` | Decoded attribute list (excludes N/A positions) |

**Methods:**

- `get_attribute(name: str) → CFIAttribute | None` — Look up an attribute by name.

### `CFIAttribute`

| Field | Type | Description |
|---|---|---|
| `position` | `int` | Character position in the code (3–6) |
| `name` | `str \| None` | Attribute name (e.g. `"voting_right"`) |
| `value` | `str \| None` | Decoded value (e.g. `"voting"`) |
| `options` | `list[str]` | All valid values (populated when `show_options=True`) |

### `CFIDecoder`

Stateless decoder class. Useful if you prefer the decoder pattern.

- `decode(cfi_code, show_options=False) → CFICode`

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
