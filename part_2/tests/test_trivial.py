import pytest


@pytest.mark.xfail
def test_divide_by_zero():
    """_summary_"""
    assert 1 / 0 == 1


def test_one_equals_one():
    """_summary_"""
    assert 1 == 1
