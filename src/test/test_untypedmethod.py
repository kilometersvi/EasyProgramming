import pytest
from easytools.decorators import untypedmethod
import inspect



# ==== Combined UntypedMethod Class Tests =====

class MyClass:
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2
    @untypedmethod('nself_arg1', nself_arg2=0)
    def foo(nself, arg1, arg2):
        return nself.arg1 + nself.arg2 + arg1 + arg2
    
    @untypedmethod('arg1')
    def foo2(nself, arg1, arg2):
        return nself.arg1 + arg1 + arg2
    
    @untypedmethod('arg1')
    def foo_with_self_kwargs(nself, arg1):
        return nself.arg1 + nself.arg2 + nself.attr


def testT1_test_foo_with_all_arguments():
    result = MyClass.foo(nself_arg1=1, nself_arg2=2, arg1=3, arg2=4)
    assert result == 10, "Test with all arguments failed"

def testT2_test_foo_with_missing_namespace_arguments():
    with pytest.raises(AttributeError):
        MyClass.foo(arg1=3, arg2=4)

def testT3_test_foo_with_extra_arguments():
    with pytest.raises(TypeError):
        MyClass.foo(nself_arg1=1, nself_arg2=2, arg1=3, arg2=4, extra_arg=5)

def testT4_test_foo_instance_method_call():
    instance = MyClass(1, 1)
    result = instance.foo(arg1=2, arg2=3)
    assert result == 7, "Instance method call failed"

def testT5_test_foo_with_incorrect_namespace_prefix():
    with pytest.raises(TypeError):
        MyClass.foo(wrong_prefix_arg1=1, arg1=3, arg2=4)



# ===== Static Signature Implementation Tests =====

class MyClass2:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @untypedmethod('arg2', 'arg1')
    def foo1(self, arg1, arg2):
        return arg1 + arg2

    @untypedmethod('arg1', arg2=4)
    def foo2(self, arg1):
        return arg1 + self.arg2

    @untypedmethod('arg1', 'arg2', arg3=6)
    def foo3(self, arg1, arg2, arg3):
        return arg1 + arg2 + arg3
    
    @untypedmethod('arg1', 'arg2', arg3=6)
    def foo4(nself, arg2):
        return nself.arg1 + arg2 + nself.arg3


def testT6_test_StaticSig__foo1_static_call():
    assert MyClass2.foo1(2, 1) == 3

def testT7_test_StaticSig__foo1_instance_call():
    instance = MyClass2()
    assert instance.foo1(1, 2) == 3

def testT8_test_StaticSig__foo2_static_call_with_default():
    assert MyClass2.foo2(1) == 5

def testT9_test_StaticSig__foo2_static_call_with_override():
    assert MyClass2.foo2(1, arg2=3) == 4

def testT10_test_StaticSig__foo2_instance_call():
    instance = MyClass2(arg2=2)
    assert instance.foo2(1) == 3

def testT11_test_StaticSig__foo3_static_call_with_all_args__kwarg_as_arg():
    assert MyClass2.foo3(1, 2, 3) == 6

def testT12_test_StaticSig__foo3_static_call_with_all_args():
    assert MyClass2.foo3(1, 2, arg3=3) == 6

def testT13_test_StaticSig__foo4_static_call():
    assert MyClass2.foo4(1, 2) == 9

def testT14_test_StaticSig__foo3_static_call_with_missing_arg():
    with pytest.raises(TypeError):
        MyClass2.foo3(1, 2)

def testT15_test_StaticSig__foo3_instance_call():
    instance = MyClass2()
    assert instance.foo3(1, 2, 3) == 6

class MyClass6:
    @untypedmethod('arg0', arg1=1)
    def test_func(nself, arg1):
        return nself.arg0 + arg1

def testT16_test_StaticSig__typeerror190():
    with pytest.raises(TypeError):
        MyClass6.test_func(2) # == 3

# ===== Inject Namespace Into Signature Implementation Tests =====

class MyClass3:
    def __init__(nself, arg1, arg2):
        nself.arg1 = arg1
        nself.arg2 = arg2

    @untypedmethod('arg1', 'arg2')
    def foo(nself):
        return nself.arg1 + nself.arg2

    @untypedmethod('arg1', 'arg2')
    def foo_with_args(nself, arg3):
        return nself.arg1 + nself.arg2 + arg3

    @untypedmethod('arg1', 'arg2')
    def foo_with_kwargs(nself, **kwargs):
        return nself.arg1 + nself.arg2 + sum(kwargs.values())

    @untypedmethod('arg1', arg2=3)  
    def foo_with_defaults(nself, arg3=5):  
        return nself.arg1 + nself.arg2 + arg3
    
    @untypedmethod('arg1', nself_arg2=3)  
    def foo_with_duplicate_names_in_nmsp_and_locals(nself, arg2=5): 
        return nself.arg1 + nself.arg2 + arg2


def testT17_test_InjectNamespace__instance_call_no_args():
    instance = MyClass3(1, 2)
    assert instance.foo() == 3

def testT18_test_InjectNamespace__instance_call_with_args():
    instance = MyClass3(1, 2)
    assert instance.foo_with_args(3) == 6

def testT19_test_InjectNamespace__instance_call_with_kwargs():
    instance = MyClass3(1, 2)
    assert instance.foo_with_kwargs(arg3=3, arg4=4) == 10

def testT20_test_InjectNamespace__instance_call_with_defaults():
    instance = MyClass3(1, 2)
    assert instance.foo_with_defaults() == 8

def testT21_test_InjectNamespace__static_call_no_args():
    assert MyClass3.foo(3, 4) == 7

def testT22_test_InjectNamespace__static_call_with_args():
    assert MyClass3.foo_with_args(3, 4, 5) == 12

def testT23_test_InjectNamespace__static_call_with_kwargs():
    assert MyClass3.foo_with_kwargs(3, 4, arg3=5, arg4=6) == 18

def testT24_test_InjectNamespace__static_call_with_defaults():
    assert MyClass3.foo_with_defaults(1) == 9

def testT25_test_InjectNamespace__static_call_with_overridden_defaults():
    assert MyClass3.foo_with_defaults(1, arg2=4) == 10

def testT26_test_InjectNamespace__static_call_mixed_args_and_kwargs():
    assert MyClass3.foo_with_kwargs(3, 4, arg3=5) == 12

def testT27_test_InjectNamespace__static_call_with_duplicate_kwargs_in_nmsp_and_locals():
    assert MyClass3.foo_with_duplicate_names_in_nmsp_and_locals(1) == 9

def testT28_test_InjectNamespace__static_call_with_duplicate_kwargs_in_nmsp_and_locals_incorrect():

    with pytest.raises(ValueError):
        class MyClass3:
            def __init__(nself, arg1, arg2):
                nself.arg1 = arg1
                nself.arg2 = arg2
            @untypedmethod('arg1', arg2=3) 
            def foo_with_duplicate_names_in_nmsp_and_locals_incorrect(nself, arg2=5, arg3=10):  
                return nself.arg1 + nself.arg2 + arg2 + arg3


#===== User Provides Dummy Instance Tests =====

class MyClass4:
    def __init__(nself, arg1, arg2):
        nself.arg1 = arg1
        nself.arg2 = arg2

    @untypedmethod()
    def foo(nself):
        return nself.arg1 + nself.arg2

    @untypedmethod()
    def foo_with_args(nself, arg3):
        return nself.arg1 + nself.arg2 + arg3

    @untypedmethod()
    def foo_with_kwargs(nself, **kwargs):
        return nself.arg1 + nself.arg2 + sum(kwargs.values())

    @untypedmethod() 
    def foo_with_defaults(nself, arg3=5):  
        return nself.arg1 + nself.arg2 + arg3
    
    @untypedmethod() 
    def foo_with_duplicate_names_in_nmsp_and_locals(nself, arg2=5): 
        return nself.arg1 + nself.arg2 + arg2


def testT29_test_UserDummy__instance_call_no_args():
    instance = MyClass4(1, 2)
    assert instance.foo() == 3

def testT30_test_UserDummy__instance_call_with_args():
    instance = MyClass4(1, 2)
    assert instance.foo_with_args(3) == 6

def testT31_test_UserDummy__instance_call_with_kwargs():
    instance = MyClass4(1, 2)
    assert instance.foo_with_kwargs(arg3=3, arg4=4) == 10

def testT32_test_UserDummy__instance_call_with_defaults():
    instance = MyClass4(1, 2)
    assert instance.foo_with_defaults() == 8

def testT33_test_UserDummy__static_call_no_args():
    assert MyClass4.foo({'arg1':3, 'arg2':4}) == 7

def testT34_test_UserDummy__static_call_with_args():
    assert MyClass4.foo_with_args({'arg1':3, 'arg2':4}, 5) == 12

def testT35_test_UserDummy__static_call_with_kwargs():
    assert MyClass4.foo_with_kwargs({'arg1':3, 'arg2':4}, arg3=5, arg4=6) == 18

def testT35_test_UserDummy__static_call_with_defaults():
    assert MyClass4.foo_with_defaults({'arg1':1, 'arg2':3}) == 9

def testT37_test_UserDummy__static_call_with_overridden_defaults():
    assert MyClass4.foo_with_defaults({'arg1':1, 'arg2':3}, arg3=6) == 10

def testT38_test_UserDummy__static_call_mixed_args_and_kwargs():
    assert MyClass4.foo_with_kwargs({'arg1':3, 'arg2':4}, arg3=5) == 12

def testT39_test_UserDummy__static_call_with_duplicate_kwargs_in_nmsp_and_locals():
    assert MyClass4.foo_with_duplicate_names_in_nmsp_and_locals({'arg1':1,'arg2':3}) == 9


class MyClass5:
    def __init__(nself, arg1, arg2):
        nself.arg1 = arg1
        nself.arg2 = arg2

    @untypedmethod
    def foo(nself):
        return nself.arg1 + nself.arg2

    @untypedmethod
    def foo_with_args(nself, arg3):
        return nself.arg1 + nself.arg2 + arg3

    @untypedmethod
    def foo_with_kwargs(nself, **kwargs):
        return nself.arg1 + nself.arg2 + sum(kwargs.values())

    @untypedmethod
    def foo_with_defaults(nself, arg3=5):  
        return nself.arg1 + nself.arg2 + arg3
    
    @untypedmethod
    def foo_with_duplicate_names_in_nmsp_and_locals(nself, arg2=5): 
        return nself.arg1 + nself.arg2 + arg2


def testT40_test_UserDummy__instance_call_no_args__no_parenthesis():
    instance = MyClass5(1, 2)
    assert instance.foo() == 3

def testT41_test_UserDummy__instance_call_with_args__no_parenthesis():
    instance = MyClass5(1, 2)
    assert instance.foo_with_args(3) == 6

def testT42_test_UserDummy__instance_call_with_kwargs__no_parenthesis():
    instance = MyClass5(1, 2)
    assert instance.foo_with_kwargs(arg3=3, arg4=4) == 10

def testT43_test_UserDummy__instance_call_with_defaults__no_parenthesis():
    instance = MyClass5(1, 2)
    assert instance.foo_with_defaults() == 8

def testT44_test_UserDummy__static_call_no_args__no_parenthesis():
    assert MyClass5.foo({'arg1':3, 'arg2':4}) == 7

def testT45_test_UserDummy__static_call_with_args__no_parenthesis():
    assert MyClass5.foo_with_args({'arg1':3, 'arg2':4}, 5) == 12

def testT46_test_UserDummy__static_call_with_kwargs__no_parenthesis():
    assert MyClass5.foo_with_kwargs({'arg1':3, 'arg2':4}, arg3=5, arg4=6) == 18

def testT47_test_UserDummy__static_call_with_defaults__no_parenthesis():
    assert MyClass5.foo_with_defaults({'arg1':1, 'arg2':3}) == 9

def testT48_test_UserDummy__static_call_with_overridden_defaults__no_parenthesis():
    assert MyClass5.foo_with_defaults({'arg1':1, 'arg2':3}, arg3=6) == 10

def testT49_test_UserDummy__static_call_mixed_args_and_kwargs__no_parenthesis():
    assert MyClass5.foo_with_kwargs({'arg1':3, 'arg2':4}, arg3=5) == 12

def testT50_test_UserDummy__static_call_with_duplicate_kwargs_in_nmsp_and_locals__no_parenthesis():
    assert MyClass5.foo_with_duplicate_names_in_nmsp_and_locals({'arg1':1,'arg2':3}) == 9

class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def testT51_test_UserDummy__static_call_no_args__no_parenthesis__namespace_passed():
    
    assert MyClass5.foo(Namespace(**{'arg1':3, 'arg2':4})) == 7

def testT52_test_UserDummy__static_call_with_args__no_parenthesis__namespace_passed():
    assert MyClass5.foo_with_args(Namespace(**{'arg1':3, 'arg2':4}), 5) == 12

def testT53_test_UserDummy__static_call_with_kwargs__no_parenthesis__namespace_passed():
    assert MyClass5.foo_with_kwargs(Namespace(**{'arg1':3, 'arg2':4}), arg3=5, arg4=6) == 18

def testT54_test_UserDummy__static_call_with_defaults__no_parenthesis__namespace_passed():
    assert MyClass5.foo_with_defaults(Namespace(**{'arg1':1, 'arg2':3})) == 9

def testT55_test_UserDummy__static_call_with_overridden_defaults__no_parenthesis__namespace_passed():
    assert MyClass5.foo_with_defaults(Namespace(**{'arg1':1, 'arg2':3}), arg3=6) == 10

def testT56_test_UserDummy__static_call_mixed_args_and_kwargs__no_parenthesis__namespace_passed():
    assert MyClass5.foo_with_kwargs(Namespace(**{'arg1':3, 'arg2':4}), arg3=5) == 12

def testT57_test_UserDummy__static_call_with_duplicate_kwargs_in_nmsp_and_locals__no_parenthesis__namespace_passed():
    assert MyClass5.foo_with_duplicate_names_in_nmsp_and_locals(Namespace(**{'arg1':1,'arg2':3})) == 9



# ===== Signature Generation Tests =====

class MyClass7:
    def __init__(nself, arg1, arg2):
        nself.arg1 = arg1
        nself.arg2 = arg2

    @untypedmethod()
    def foo_dummy(nself):
        return nself.arg1 + nself.arg2
        
    @untypedmethod
    def foo_dummy2(nself):
        return nself.arg1 + nself.arg2
    
    @untypedmethod
    def foo_dummy3(nself, arg3):
        return nself.arg1 + nself.arg2 + arg3

    @untypedmethod('arg0', arg1=1)
    def foo_full_static(nself, arg1):
        return nself.arg1 + arg1

    @untypedmethod('arg0')
    def foo_namespace_injection(nself, arg1):
        return nself.arg1 + arg1

def testT58_test_dummy_insert_mode_signature_static():
    static_callable = MyClass7.foo_dummy
    instance_callable = MyClass7(None, None).foo_dummy

    assert 'assert1'+str(inspect.signature(static_callable)) == 'assert1'+"(nself)"
    assert 'assert2'+str(inspect.signature(instance_callable)) == 'assert2'+"()"


def testT59_test_dummy_insert_mode_signature_static_multiple_params():
    static_callable = MyClass7.foo_dummy3
    instance_callable = MyClass7(None, None).foo_dummy3

    assert str(inspect.signature(static_callable)) == "(nself, arg3)"
    assert str(inspect.signature(instance_callable)) == "(arg3)"

def testT60_test_dummy_insert_mode_signature_no_parenthesis():
    static_callable = MyClass7.foo_dummy2
    instance_callable = MyClass7(None, None).foo_dummy2

    assert str(inspect.signature(static_callable)) == "(nself)"
    assert str(inspect.signature(instance_callable)) == "()"

def testT61_test_full_static_signature_mode_signature():
    static_callable = MyClass7.foo_full_static
    instance_callable = MyClass7(None, None).foo_full_static

    assert str(inspect.signature(static_callable)) == "(nself_arg0, arg1=1)"
    assert str(inspect.signature(instance_callable)) == "(arg1)"

def testT62_test_namespace_injection_mode_signature():
    static_callable = MyClass7.foo_namespace_injection
    i = MyClass7(None, None)
    instance_callable = i.foo_namespace_injection

    assert str(inspect.signature(static_callable)) == "(nself_arg0, arg1)"
    assert str(inspect.signature(instance_callable)) == "(arg1)"





if __name__ == "__main__":
    pytest.main()

