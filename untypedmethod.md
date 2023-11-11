# The `untypedmethod` Decorator

## Overview

The `untypedmethod` decorator is a versatile tool designed to enhance the flexibility of method definitions in Python classes. It allows methods to be called either as instance methods or static methods, with various ways of handling arguments and namespace attributes. This decorator is particularly useful in scenarios where the same method needs to be used in different contexts, either with an instance of the class or without it.

## Key Features

- **Dynamic Signature Handling:** Allows methods to adapt their signatures based on the context of the call (instance or static).
- **Namespace Injection:** Facilitates the injection of namespace attributes into the method's signature, enhancing flexibility.
- **Argument Parsing:** Efficiently and intelligently parses and routes arguments to their appropriate destinations, whether they are part of the instance's namespace or the method's parameters.
- **Error Handling:** Provides clear error messages for common issues such as unexpected arguments or conflicts between namespace attributes and method parameters.

## Usage

The `untypedmethod` decorator can be used in several modes, each catering to different use cases:

1. **Pass Dummy Instances, Namespaces, or Key-Value Pairs as `self`:** When no arguments are configured in the decorator, `untypedmethod` acts as a specifier, indicating that when the function is called statically, the first argument (in place of `self`) should be either a dictionary or namespace object. If a dictionary is passed, the namespace will be generated from the dictionary.

2. **Define Alternative Signatures:** If all parameters in the function signature are defined in the decorator's arguments, the decorator's arguments are treated as an alternate signature, used for static calls.

3. **Modify Existing Signatures:** If not all parameters from the function signature are defined in the decorator's arguments, the decorator arguments define the parameters accessible through the namespace. This mode allows for a mix of namespace attributes and regular parameters in the method signature.


## Basic Usage

### Simple Example

```python

from easytools.decorators import untypedmethod

class MyClass:
    def __init__(self, arg1):
        self.arg1 = arg1

    @untypedmethod
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

    @untypedmethod
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
    @untypedmethod('separator', do_caps=True)
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


### Specifying Namespace Attributes

The decorator can be used to explicitly define which arguments should be treated as namespace attributes, in the case that both an attribute and parameter exists with this name.

```python
class MyClass:
    @untypedmethod('nself_arg1', nself_arg2=0)
    def add(nself, arg1, arg2):
        return nself.arg1 + nself.arg2 + arg1 + arg2

# Static method call
print(MyClass.add(1, 2, 3, 4))  # Output: 10
```

In this case, `nself_arg1` and `nself_arg2` are treated as namespace attributes. They are converted to attributes `nself.arg1` and `nself.arg2`, respectively.

The prefix is generated from the parameter corresponding with the `self` position. For example, if the parameter `foo` was used as the first parameter in the method definition, the prefix would then be `foo_`:

```python
class MyClass:
    @untypedmethod('foo_arg1')
    def add(foo, arg1):
        return foo.arg1 + arg1

# Static method call
print(MyClass.add(1, 2))  # Output: 3
```


### Alternative Function Signatures

We can take this a step further by repeatedly defining all the parameters and default parameters from the function in the arguments to `untypedmethod`.

```python
class MyClass:
    @untypedmethod('arg1', 'arg2', 'attr1', 'nself.attr2', attr3=3)
    def add(nself, arg1, arg2):
        return arg1 + arg2 + nself.attr1 + nself.attr2 + nself.attr3

# Static method call
print(MyClass.add(1, 2, 3, 4, 5))  # Output: 15
```

Now, we have 2 readable signatures for this function- the arguments in the decorator (for static calls), and the regular function signature (for instance calls). 

It is implied that all function parameters must be specified in the decorator arguments for this to occur.

The `nself` prefix can be used in this application as well. This is useful for increasing readability in cases where it is important to know how a parameter will be used by the static call to a function.


### `inspect` Compatibility

Python's `inspect` library will see these updated functions signatures:

```python
class MyClass:
    def __init__(nself, arg1, arg2):
        nself.arg1 = arg1
        nself.arg2 = arg2
    
    @untypedmethod
    def foo(nself, arg3):
        return nself.arg1 + nself.arg2 + arg3

    static_callable = MyClass.foo
    instance_callable = MyClass7(None, None).foo

    print(str(inspect.signature(static_callable))) # Output: "(nself, arg3)"
    print(str(inspect.signature(instance_callable))) # Output: "(arg3)"
```

This feature holds true with any application of `untypedmethod`

## Applications

### Converting Instance Functions to Static Functions

The `untypedmethod` decorator can be used to convert static functions into instance functions without modifying the function's code. This is particularly useful for adapting existing code to new requirements, for allowing static calls to instance functions without creating a near-similar function, or for making code cleaner.

### Avoid Repetitive Functions or Modifying Existing Functions

With this decorator, you can avoid creating new static versions of your functions, removing the need for duplicate code in some instances. Just as well, you can now skip modifying functions to make them into staticmethods.

### Simplifying Method Signatures

By using namespace attributes, you can simplify method signatures and avoid repetitive argument passing, especially when several methods share common parameters.

## Testing

The provided tests demonstrate the capabilities of the `untypedmethod` decorator in various scenarios, including handling of default values, namespace attributes, and error handling.

## Conclusion

The `untypedmethod` decorator offers a powerful way to write flexible and reusable methods in Python. Its ability to handle different calling contexts and argument types makes it a valuable tool for various programming needs.