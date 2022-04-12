import pytest
def add(a,b):
    return a+b

def test_add_01():
    assert add(1,2)==3

def test_add_02():
    assert add(2,3)==5

def test_add_03():
    assert add(2,3)==5