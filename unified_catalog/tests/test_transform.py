import json
from unified_catalog.transform import parse_json_field, merge_unique_lists, normalize_level, parse_weeks

def test_parse_json_field_variants():
    assert parse_json_field(None) == []
    assert parse_json_field(["A", "a", "B"]) == ["A", "a", "B"]
    assert parse_json_field('["x","y","x"]') == ["x", "y"]
    assert parse_json_field("x, y ; z|x") == ["x", "y", "z", "x"][:3]  # dedup keeps first x

def test_merge_unique_lists():
    a = ["AI", "ML", "ai"]
    b = ["Data", "ml", "NLP"]
    assert merge_unique_lists(a, b) == ["AI", "ML", "Data", "NLP"]

def test_normalize_level():
    assert normalize_level("Beginner") == "beginner"
    assert normalize_level("ADVANCED track") == "advanced"
    assert normalize_level("Something else") == "Something else"

def test_parse_weeks():
    assert parse_weeks(6) == 6
    assert parse_weeks("6 weeks") == 6
    assert parse_weeks("Approx. 8 Weeks") == 8
    assert parse_weeks("2-4 weeks") == 4
    assert parse_weeks("N/A") is None
