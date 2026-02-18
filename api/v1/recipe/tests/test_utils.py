import pytest
from api.v1.recipe.utils.helpers import UnitConverter, clean_name
from recipe.choices import Unit

@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("яблоко", "яблоко"),
        ("  яблоко  ", "яблоко"),
        ("яблоко!!!", "яблоко"),
        ("яблоко, банан", "яблоко банан"),
        ("яблоко123", "яблоко123"),
        ("!@#$%^&*()", ""),
        ("  multiple   spaces ", "multiple spaces"),
    ]
)
def test_clean_name(input_str, expected):
    assert clean_name(input_str) == expected


@pytest.mark.parametrize(
    "amount, raw_unit, expected_amount, expected_unit",
    [
        (1, "oz", 28.35, Unit.GR),
        (2, "ounce", 56.70, Unit.GR),
        (1.5, "ounces", 42.52, Unit.GR),
        (1, "lb", 453.59, Unit.GR),
        (2, "lbs", 907.18, Unit.GR),
        (1, "pound", 453.59, Unit.GR),
        (2.5, "pounds", 1133.98, Unit.GR),
        (1, "unknown", 1, "unknown"),
        (None, "lb", None, "lb"),
        (1, None, 1, None),
    ]
)
def test_unit_converter_convert(amount, raw_unit, expected_amount, expected_unit):
    result_amount, result_unit = UnitConverter.convert(amount, raw_unit)

    if isinstance(result_amount, float) or isinstance(expected_amount, float):
        assert round(result_amount, 2) == round(expected_amount, 2)
    else:
        assert result_amount == expected_amount

    assert result_unit == expected_unit
