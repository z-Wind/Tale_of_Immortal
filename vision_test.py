import vision
import pytest


def test_hollow_rectangle():
    result = vision.Vision.hollow_rectangle((0, 0, 10, 10), (1, 2, 5, 5))
    assert result == ((0, 0, 10, 2), (0, 2, 1, 5), (6, 2, 4, 5), (0, 7, 10, 3))

    result = vision.Vision.hollow_rectangle((0, 0, 10, 10), (1, 2, 0, 0))
    assert result == ((0, 0, 10, 10),)

    with pytest.raises(AssertionError):
        result = vision.Vision.hollow_rectangle((1, 2, 5, 5), (0, 0, 10, 10))
