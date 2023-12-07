# The `flexmethod` Decorator

## Overview

The `flexmethod` decorator is a versatile tool designed to enhance the flexibility of method definitions in Python classes. It allows methods to be called either as instance methods or static methods, with various ways of handling arguments and namespace attributes. This decorator is particularly useful in scenarios where the same method needs to be used in different contexts, either with an instance of the class or without it.

```python
from types import SimpleNamespace

class MyClass:
    def __init__(self, num1, num2):
        self.num1 = num1
        self.num2 = num2

    @flexmethod.nsinsert
    def new_namespace_when_static(nself, num2):
        return nself.num1 + num2
    
    @flexmethod.nssync('num1', 'num2')
    def longer_signature_when_static(nself, num3):
        return nself.num1 + nself.num2 + num3
    
    @flexmethod.staticsig('num1','num2','num3')
    def full_static_signature_given(nself, num3):
        return nself.num1 + nself.num2 + num3
        

# Instance method call of nsinsert method
instance = MyClass(5, 1)
print(instance.new_namespace_when_static(3))  # Output: 8

# Static method call of nsinsert method
my_namespace = SimpleNamespace(**{'num1': 5})
print(MyClass.new_namespace_when_static(my_namespace, 3))  # Output: 8

# Instance method call of nssync method
print(instance.longer_signature_when_static(2))  # Output: 8

# Static method call of nssync method
print(MyClass.longer_signature_when_static(5, 1, 2))  # Output: 8

# Instance method call of staticsig method
print(instance.full_static_signature_given(3))  # Output: 8

# Static method call of staticsig method
print(MyClass.full_static_signature_given(5, 1, 2))  # Output: 8
```

## Key Features

- **Dynamic Signature Handling:** Allows methods to adapt their signatures based on the context of the call (instance or static).
- **Namespace Injection:** Facilitates the injection of namespace attributes into the method's signature, enhancing flexibility.
- **Intuitive Behavior:** Intended behavior for the method is understood by the `flexmethod` base class.
- **Argument Parsing:** Efficiently and intelligently parses and routes arguments to their appropriate destinations, whether they are part of the instance's namespace or the method's parameters.
- **Error Handling:** Provides clear error messages for common issues such as unexpected arguments or conflicts between namespace attributes and method parameters.

## Usage

The `flexmethod` decorator can be used in several modes, each catering to different use cases:

1. **Pass Dummy Instances, Namespaces, or Key-Value Pairs as `self`:** When no arguments are configured in the decorator, `flexmethod` acts as a specifier, indicating that when the function is called statically, the first argument (in place of `self`) should be either a dictionary or namespace object. If a dictionary is passed, the namespace will be generated from the dictionary.

2. **Define Alternative Signatures:** If all parameters in the function signature are defined in the decorator's arguments, the decorator's arguments are treated as an alternate signature, used for static calls.

3. **Modify Existing Signatures:** If not all parameters from the function signature are defined in the decorator's arguments, the decorator arguments define the parameters accessible through the namespace. This mode allows for a mix of namespace attributes and regular parameters in the method signature.


## Basic Usage

### Simple Example

```python

from easytools.flexmethod import flexmethod

class MyClass:
    def __init__(self, arg1):
        self.arg1 = arg1

    @flexmethod
    def add(nself, arg2):
        return nself.arg1 + arg2

# Instance method call
instance = MyClass(5)
print(instance.add(3))  # Output: 8

# Static method call
print(MyClass.add({'arg1': 5}, 3))  # Output: 8
```

In this example, the `add` method can be called both as an instance method and a static method. When called statically, the first argument is a dictionary representing the instance attributes.

Also of note, when defining an untyped method, `nself` (namespace self) is typically used instead of `self`, though this is not enforced.

### Pass Namespace To Function in place of Self in Static Calls

```python
from types import SimpleNamespace

class MyClass:
    def __init__(self, arg1):
        self.arg1 = arg1

    @flexmethod
    def add(nself, arg2):
        return nself.arg1 + arg2


# Instance method call
instance = MyClass(5)
print(instance.add(3))  # Output: 8

# Static method call
my_namespace = SimpleNamespace(**{'arg1': 5})
print(MyClass.add(my_namespace, 3))  # Output: 8
```
Namespaces can be generated beforehand, and passed to an untyped function in this manner as well.

### Define Namespace Attributes in Signature

Namespace attributes can be defined in the decorator's arguments, and will then become available as parameters.

```python
class MyClass:
    @flexmethod('separator', do_caps=True)
    def concat(nself, end, **kwargs):
        combined = nself.separator.join(kwargs.values()) + end
        
        if nself.do_caps:
            combined.capitalize()
        
        return combined

# Static method call
print(MyClass.concat(' ', '!', arg1 ='attribute', \
    arg2='defined in', arg3='signature'))  
# Output: Attribute defined in signature!
```

Positional parameters from the decorator will be inserted before the positional arguments in the function.


Although `flexmethod` can intuit the desired behavior of its use, this namespace attribute augmentation of the function signature can be explicity stated using `@flexmethod.nssync` (namespace-signature synchronization):

```python
class MyClass:
    @flexmethod.nssync('num1')
    def add(nself, num2):
        return nself.num1 + num2
```

### Specifying Namespace Attributes

The decorator can be used to explicitly define which arguments should be treated as namespace attributes, in the case that both an attribute and parameter exists with this name.

```python
class MyClass:
    @flexmethod('nself_arg1', nself_arg2=0)
    def add(nself, arg1, arg2):
        return nself.arg1 + nself.arg2 + arg1 + arg2

# Static method call
print(MyClass.add(1, 2, 3, 4))  # Output: 10
```

In this case, `nself_arg1` and `nself_arg2` are treated as namespace attributes. They are converted to attributes `nself.arg1` and `nself.arg2`, respectively.

The prefix is generated from the parameter corresponding with the `self` position. For example, if the parameter `foo` was used as the first parameter in the method definition, the prefix would then be `foo_`:

```python
class MyClass:
    @flexmethod('foo_arg1')
    def add(foo, arg1):
        return foo.arg1 + arg1

# Static method call
print(MyClass.add(1, 2))  # Output: 3
```

### Alternative Function Signatures

We can take this a step further by repeatedly defining all the parameters and default parameters from the function in the arguments to `flexmethod`.

```python
class MyClass:
    @flexmethod('arg1', 'arg2', 'attr1', 'nself.attr2', attr3=3)
    def add(nself, arg1, arg2):
        return arg1 + arg2 + nself.attr1 + nself.attr2 + nself.attr3

# Static method call
print(MyClass.add(1, 2, 3, 4, 5))  # Output: 15
```

Now, we have 2 readable signatures for this function- the arguments in the decorator (for static calls), and the regular function signature (for instance calls). 

It is implied that all function parameters must be specified in the decorator arguments for this to occur.

The `nself` prefix can be used in this application as well. This is useful for increasing readability in cases where it is important to know how a parameter will be used by the static call to a function.

### Explicitly stating behavior

Although `flexmethod` can intuit the desired behavior of its use, its intended use can be explicitly stated to increase readability. 


For the augmentation of a function signature by turning the `self` parameter into one available for use in passing namespaces, this behavior can be explicity stated using `@flexmethod.nsinsert` (namespace insertion).

For the augmentation of a function signature by adding namespace attributes as arguments, this behavior can be explicity stated using `@flexmethod.nssync()` (namespace-signature synchronization).

For the use case where `flexmethod` contains the full alternate signature for when the function is called statically, use `@flexmethod.staticsig()`

```python
from types import SimpleNamespace

class MyClass:
    def __init__(self, num1, num2):
        self.num1 = num1
        self.num2 = num2

    @flexmethod.nsinsert
    def new_namespace_when_static(nself, num2):
        return nself.num1 + num2
    
    @flexmethod.nssync('num1', 'num2')
    def longer_signature_when_static(nself, num3):
        return nself.num1 + nself.num2 + num3
    
    @flexmethod.staticsig('num1','num2','num3')
    def full_static_signature_given(nself, num3):
        return nself.num1 + nself.num2 + num3
        

# Instance method call of nsinsert method
instance = MyClass(5, 1)
print(instance.new_namespace_when_static(3))  # Output: 8

# Static method call of nsinsert method
my_namespace = SimpleNamespace(**{'num1': 5})
print(MyClass.new_namespace_when_static(my_namespace, 3))  # Output: 8

# Instance method call of nssync method
print(instance.longer_signature_when_static(2))  # Output: 8

# Static method call of nssync method
print(MyClass.longer_signature_when_static(5, 1, 2))  # Output: 8

# Instance method call of staticsig method
print(instance.full_static_signature_given(3))  # Output: 8

# Static method call of staticsig method
print(MyClass.full_static_signature_given(5, 1, 2))  # Output: 8
```

### Variable Injection

For now, you can determine if your function was called statically or dynamically within the scope of your function by accessing `nself.__static_from_flexmethod__`. It is planned to move this to a variable outside of the scope of nself to not leave litter on instances.

### `inspect` Compatibility

Python's `inspect` library will see these updated functions signatures:

```python
class MyClass:
    def __init__(nself, arg1, arg2):
        nself.arg1 = arg1
        nself.arg2 = arg2
    
    @flexmethod
    def foo(nself, arg3):
        return nself.arg1 + nself.arg2 + arg3

    static_callable = MyClass.foo
    instance_callable = MyClass7(None, None).foo

    print(str(inspect.signature(static_callable))) # Output: "(nself, arg3)"
    print(str(inspect.signature(instance_callable))) # Output: "(arg3)"
```

This feature holds true with any application of `flexmethod`

## Applications

### Converting Instance Functions to Static Functions

The `flexmethod` decorator can be used to convert static functions into instance functions without modifying the function's code. This is particularly useful for adapting existing code to new requirements, for allowing static calls to instance functions without creating a near-similar function, or for making code cleaner.

### Avoid Repetitive Functions or Modifying Existing Functions

With this decorator, you can avoid creating new static versions of your functions, removing the need for duplicate code in some instances. Just as well, you can now skip modifying functions to make them into staticmethods.

### Simplifying Method Signatures

By using namespace attributes, you can simplify method signatures and avoid repetitive argument passing, especially when several methods share common parameters.

## Testing

The provided tests demonstrate the capabilities of the `flexmethod` decorator in various scenarios, including handling of default values, namespace attributes, and error handling.

## Conclusion

The `flexmethod` decorator offers a powerful way to write flexible and reusable methods in Python. Its ability to handle different calling contexts and argument types makes it a valuable tool for various programming needs.

## Current bugs/Todo:
- Signatures not always correct on instances
- Static functions not correctly processing variable keyword parameters (ex: '**kwargs')
- Wrong parameter order for instance calls to functions with variable keyword parameters
- Still has debugging on
- Implement flexmethod.parambind: convert static methods to instance methods (from untypedmethod)
- Allow use of scoped variables in decorator arguments (ie can do @flexmethod(cls.argname, f"arg2={self.arg2}"))
