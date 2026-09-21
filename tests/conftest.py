import pytest

from zimmteb.datasets.registry import load_dataset


@pytest.fixture
def tiny():
    return load_dataset()
