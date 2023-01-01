import pytest

def f(i):
    return i + 1

def test_f():
    assert f(1) == 2

def test_p():
    assert f(1) == 3
