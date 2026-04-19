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
