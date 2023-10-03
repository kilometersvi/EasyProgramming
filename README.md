# easytools

a bunch of classes and functions i use in stuff sometimes

includes:
- untyped: a decorator for making instance functions act both static and dynamic depending on context
- adjumerate: adjustable enumerate-like iterable
- unique_token: unique token generator

## install

```
pip3 install git+https://github.com/kilometersvi/easytools.git
```

## docs

### untyped decorator

prevent instantiating objects for a single function call, while also avoiding overloading functions to make them compatible for both static and dynamic purposes.

switch from this:

```
class MyClass:
    def __init__(self):
        pass

    def foo(self, arg1, arg2):
        return arg1 + arg2

c = MyClass() # <-- unnesseccary instantiation :(
print c.foo(1,2)

```

and this:

```
class MyClass:
    def __init__(self, attr1, attr2):
        self.attr1 = attr1
        self.attr2 = attr2

    def foo(self, arg1=None, arg2=None):

        # confusing and not very readable :(

        if arg1 is None and arg2 is None:
            return self.attr1 + self.attr2

        elif isinstance(arg1, (int, float)) and isinstance(arg2, (int, float)):
            return arg1 + arg2
        else:
            raise ValueError("Invalid arguments provided")

    @staticmethod
    def foo_static(arg1, arg2): # <-- different function names for static vs dynamic access :(

        return arg1 + arg2

my_instance = MyClass(1, 2)
print(f"dynamic foo: {c.foo()} == 3")
print(f"static foo: {MyClass.foo_static(3, 4)} == 7")
print(f"dynamic foo with only args: {c.foo(3, 4)} == 7")

```

to this:

```
from easytools.adaptive_method import untyped

class MyClass:
    def __init__(self, attr1, attr2):
        self.attr1 = attr1
        self.attr2 = attr2

    @untyped({"arg1": "attr1", "arg2": "attr2"})
    def foo(self, arg1, arg2=20):
        return arg1 + arg2

my_instance = MyClass(1,2)

print(f"dynamic foo: {my_instance.foo(5, 5)} == 10")
print(f"static foo: {MyClass.foo(5, 5)} == 10")
print(f"dynamic foo, with instance attributes as arguments: {my_instance.foo()} == 3")
print(f"dynamic foo, with instance attribute argument positioning: {my_instance.foo(arg2 = 4)} == 5")
print(f"static foo, with default argument positioning: {MyClass.foo(5)} == 25")
```

you can also use a list instead of dict, assuming parameter names and instance attr names are identical:

```
class MyClass:
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2

    @untyped(["arg1", "arg2"])
    def foo(self, arg1, arg2):
        return arg1 + arg2

```

you can also use a list with the inverse parameter to map all matching parameters/instance attributes pairs except the ones included in list:

```
class MyClass:
    def __init__(self, arg1, arg2, not_for_funct):
        self.arg1 = arg1
        self.arg2 = arg2
        self.not_for_funct = not_for_funct

    @untyped(["not_for_funct"], inverse=True)
    def foo(self, arg1, arg2):
        return arg1 + arg2
```

### adjumerate (adjustable enumerating iterable)

adjust the index returned by enumerate to act as a adjustable counter. makes code look a little more pleasant.

switch from this:

```
i = 0 # <-- why do we still need to do this?
for x in range(10):
    if not i%7:
        i = 0
    if i == 4:
        i += 1
    i += 1 # <-- i want the loop to handle this...
```

to this:

```
from easytools.adjumerate import adjumerate

for i, x in adjumerate(range(10), start=0):
    if not i%7:
        i.set(0)
    if i == 4:
        i += 1
    print(f"been here for {i.raw} entire iters, but my count is at {i}")
```

### unique token handler

generate unique tokens that wouldn't possibly end up in your corpus.

```
from easytools.unique_token import UniqueTokenHandler

u = UniqueTokenHandler()

token = u.generate()
print(f'{token} probably looks like "$̶͇̖͍̹͈̮̦͙͔̗͈͉͖̬̪̌͌͐͊̀̎͌̀́̓͋̎̎̾̈́̍̔̽̕͝͝ͅ"')
id = u.get(token)
print(f"this token's id is {id}. and in case you forgot, the token is {u.get(id)}")
```
