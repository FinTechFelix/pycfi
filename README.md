# CFI Code Decoder

A Python package for decoding **CFI codes** based on the ISO 10962 standard. Translates 6-character CFI codes into structured, human-readable descriptions of financial instruments.

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

## Usage

### Quickest: module-level function

```python
from pycfi import decode

code = decode("ESVUFR")
print(code.category)   # "equity"
print(code.group)      # "common/ordinary shares"
```

### Object-oriented: CFICode

```python
from pycfi import CFICode

code = CFICode("RWSNCA")
print(code.category)   # "entitlements"
print(code.group)      # "warrants"

attr = code.get_attribute("underlying_assets")
print(attr.value)      # "equities"
```

### Decoder pattern: CFIDecoder

```python
from pycfi import CFIDecoder

decoder = CFIDecoder()
code = decoder.decode("ESVUFR")
```

### Accessing attributes

Attributes are available as a list of `CFIAttribute` objects:

```python
code = decode("ESVUFR")

for attr in code.attributes:
    print(attr.position, attr.name, attr.value)
# 3 voting_right voting
# 4 ownership free
# 5 payment_status fully paid
# 6 form registered

# Or look up by name directly
voting = code.get_attribute("voting_right")
print(voting.value)    # "voting"
print(voting.position) # 3
```

### Showing available options

Pass `show_options=True` to include all valid values for each attribute position:

```python
code = decode("ESVUFR", show_options=True)
voting = code.get_attribute("voting_right")
print(voting.options)
# ["voting", "non-voting", "restricted", "enhanced voting"]
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
| `attributes` | `list[CFIAttribute]` | Decoded attribute list |

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

## Example

```python
from pycfi import decode

code = decode("RWSNCA")
print(code)
# CFICode('RWSNCA', category='entitlements', group='warrants')

for attr in code.attributes:
    print(f"  [{attr.position}] {attr.name}: {attr.value}")
# [3] underlying_assets: equities
# [4] type: naked warrants
# [5] call_put: call
# [6] exercise_option_style: american
```

---

## License

MIT
