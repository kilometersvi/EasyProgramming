import pytest
import easytools
from easytools.adaptive_method import untyped, MyClass 

def test_functions():
    c = MyClass(1, 2)

    # Test method signatures
    assert str(inspect.signature(c.foo)) == "(self, arg1, arg2=None)"

    # Test the behavior of the methods
    assert c.foo(5, 5) == 10
    assert c.foo2(5, 5) == 0
    assert c.foo(arg2=15) == 16
    assert c.foo2(attribute2=15) == -14
    assert MyClass.foo(10, 10) == 20
    assert MyClass.foo2(10, 10) == 0
    assert c.foo3() == 13
    assert MyClass.foo3(2) == 26
