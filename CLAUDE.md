# pycfi

Python library for reading ISO 10962 CFI (Classification of Financial Instruments) codes.

## Project structure

```
src/pycfi/
  __init__.py       # Exports CFICode and CFIAttribute
  decoder.py        # CFICode class and CFIAttribute dataclass
  map.py            # ISO 10962 lookup tables (CATEGORY_MAP, GROUP_MAP, ATTRIBUTE_MAP)
tests/
  test_decoder.py   # pytest test suite (also has an interactive __main__ runner)
```

## Public API

There are exactly two public types, both exported from `pycfi`:

- **`CFICode(code: str, show_options: bool = False)`** — the main class. Pass a 6-character CFI code string. Decoded fields: `.raw`, `.category`, `.group`, `.attributes`. Use `.get_attribute(name)` for lookup by name. `print(code)` shows the full human-readable breakdown.
- **`CFIAttribute`** — dataclass with `.position`, `.name`, `.value`, `.options`.

There is no `decode()` function or `CFIDecoder` class. `CFICode` is the only interface.

## Usage

```python
from pycfi import CFICode

code = CFICode("ESVUFR")
code.category                            # "equity"
code.group                               # "common/ordinary shares"
code.get_attribute("voting_right").value  # "voting"
print(code)                              # full human-readable breakdown
```

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pytest tests/test_decoder.py -v
```

## Key conventions

- All decoded values are returned in lowercase.
- N/A placeholder attributes (e.g. `na_1`, `na_2` in `map.py`) are filtered out from `CFICode.attributes` — they are internal to the mapping tables only.
- Unknown/unrecognised characters return `None` values, not errors. Only structurally invalid codes (wrong type or wrong length) raise `ValueError`.
- `map.py` contains the raw ISO 10962 lookup tables. Do not modify attribute names in `map.py` without updating the tests.
