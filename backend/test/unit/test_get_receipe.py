import pytest
import pytest_cov
import unittest.mock as mock
from src.controllers.receipecontroller import ReceipeController, Diet


@pytest.fixture
def sut():
    mocked_calculate_readiness = mock.MagicMock()

    def calculate_readiness_side_effect(receipe, available_items):
        required_items = receipe['ingredients']
        return sum(available_items.get(item, 0) for item in required_items) / len(required_items)

    mocked_calculate_readiness.side_effect = calculate_readiness_side_effect
    sut = ReceipeController(mocked_calculate_readiness)
    return sut


@pytest.mark.unit
@pytest.mark.parametrize("receipe, available_items, diet", [
    ({"diets": ["diet1"]}, {}, Diet("diet2"))
])
def test_receipe_not_following_diet(sut, receipe, available_items, diet):
    readiness = sut.get_receipe_readiness(receipe, available_items, diet)
    assert readiness is None


@pytest.mark.unit
@pytest.mark.parametrize("receipe, available_items, diet", [
    ({"diets": ["diet1"]}, {}, Diet("diet1"))
])
def test_no_available_items(sut, receipe, available_items, diet):
    readiness = sut.get_receipe_readiness(receipe, available_items, diet)
    assert readiness is None


@pytest.mark.unit
@pytest.mark.parametrize("receipe, available_items, diet", [
    ({"diets": ["diet1"], "ingredients": ["apple", "orange"]},
     {"apple": 1, "orange": 1}, Diet("diet1"))
])
def test_all_required_items(sut, receipe, available_items, diet):
    readiness = sut.get_receipe_readiness(receipe, available_items, diet)
    assert readiness > 0.1


@pytest.mark.unit
@pytest.mark.parametrize("receipe, available_items, diet", [
    ({"diets": ["diet1"], "ingredients": ["apple", "orange", "tomato"]}, {
     "apple": 1, "orange": 1}, Diet("diet1"))
])
def test_some_required_items(sut, receipe, available_items, diet):
    readiness = sut.get_receipe_readiness(receipe, available_items, diet)
    assert readiness is None


@pytest.mark.unit
@pytest.mark.parametrize("receipe, available_items, diet", [
    ({"diets": ["diet1"], "ingredients": ["apple", "orange", "tomato"]}, {
     "apple": 1, "orange": 1, "tomato": 1}, Diet("diet1"))
])
def test_low_readiness(sut, receipe, available_items, diet):
    sut.calculate_readiness = mock.MagicMock(return_value=0.05)
    readiness = sut.get_receipe_readiness(receipe, available_items, diet)
    assert readiness is None


@pytest.mark.unit
@pytest.mark.parametrize("receipe, available_items, diet", [
    ({"diets": ["diet1"], "ingredients": ["apple", "orange"]},
     {"apple": 1, "orange": 1}, "invalid_diet")
])
def test_invalid(sut, receipe, available_items, diet):
    with pytest.raises(TypeError):
        sut.get_receipe_readiness(receipe, available_items, diet)
