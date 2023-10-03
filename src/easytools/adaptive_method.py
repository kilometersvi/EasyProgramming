import inspect
from functools import wraps
from easytools.adjumerate import adjumerate
from easytools.unique_token import UniqueTokenHandler

def is_instance_of_method(obj, method):
    return hasattr(method, '__self__') and isinstance(obj, method.__self__.__class__)

def arg_formatter(parameters_dict, f_args, f_kwargs, preseded_args_dict=None, remove_first=True):
    """
    parameters_dict = parameters of function (consider function.sig.parameters). use these for defaults
    f_args = arguments passed to function in call
    f_kwargs = keyword arguments passed to function in call
    preseded_args_dict = dict containing parameters to use values from this dict for ({parameter:argument}). these are superseded by f_args and f_kwargs.
    """

    u = UniqueTokenHandler()
    t = u.generate()

    parameters = list(parameters_dict.keys())[remove_first:]
    new_args = [t] * len(parameters)
    new_kwargs = f_kwargs.copy()

    #set defaults
    for i, p in enumerate(parameters):
        if parameters_dict[p].default != inspect.Parameter.empty:
            new_args[i] = parameters_dict[p].default

    #insert lesser priority args
    if preseded_args_dict:
        for i, p in enumerate(parameters):
            if p in preseded_args_dict.keys():
                new_args[i] = preseded_args_dict[p]

    #replace with args
    for i, p in adjumerate(parameters):
        if p in new_kwargs:
            new_args[i.raw] = new_kwargs[p]
            del new_kwargs[p]
            i -= 1
        else:
            try:
                new_args[i.raw] = f_args[i]
            except IndexError as e:
                pass

    #ensure all positions are filled
    if t in new_args:
        return None, new_args.index(t)

    return new_args, new_kwargs



def untyped(param_to_instance_attr_map=None, inverse=False):
    """
    param_to_instance_attr_map = class variables to use as arguments at parameter.
        either list([var1,var2]) where var names equal parameter names, or dict({param1:ivar1,param2:ivar2,...})
    inverse = when providing list, will treat list as list of all parameters to avoid using instance vars for
    """
    class AdaptiveMethod:
        def __init__(self, func):
            self.func = func
            self.sig = inspect.signature(func)

        def __get__(self, instance, owner):
            @wraps(self.func)
            def bound_method(*args, **kwargs):
                # If called as an instance method
                if instance is not None:
                    parameters = list(self.sig.parameters.keys())[1:]  # Skip 'self'

                    # build instance args list
                    i_param_dict = {}

                    #no instancevardict provided; assume standard naming of parameter = class var name
                    if not param_to_instance_attr_map:
                        for p in parameters:
                            if p in dir(instance):
                                i_param_dict[p] = instance.__getattribute__(p)

                    #list provided; assume standard naming of parameter = class var name
                    if isinstance(param_to_instance_attr_map, list):
                        if not inverse:
                            for p in param_to_instance_attr_map:
                                if p in parameters:
                                    i_param_dict[p] = instance.__getattribute__(p)
                                else:
                                    raise AttributeError(f"{self.func.__name__}() has no parameter '{p}'")
                        else:
                            for p in parameters:
                                if p not in param_to_instance_attr_map:
                                    try:
                                        i_param_dict[p] = instance.__getattribute__(p)
                                    # parameter not filled by any of instance var, parameter default, or argument
                                    except AttributeError as ae:
                                        if p not in kwargs.keys() and self.sig.parameters[p].default == inspect.Parameter.empty:
                                            raise TypeError(f"{self.func.__name__}() missing at least 1 required positional argument: '{p}'")


                    #map provided
                    if isinstance(param_to_instance_attr_map, dict):
                        for p in param_to_instance_attr_map.keys():
                            if p not in parameters:
                                raise AttributeError(f"{self.func.__name__}() has no parameter '{p}'")
                            i_param_dict[p] = instance.__getattribute__(param_to_instance_attr_map[p])


                    o = arg_formatter(self.sig.parameters, args, kwargs, preseded_args_dict=i_param_dict, remove_first=True)
                    if o[0] == None:
                        raise TypeError(f"{self.func.__name__}() missing at least 1 required positional argument: '{parameters[o[1]]}'")

                    new_args, new_kwargs = o

                    return self.func(instance, *new_args, **new_kwargs)

                # If called as a static method
                else:
                    return self.func(None, *args, **kwargs)

            return bound_method

    return AdaptiveMethod


# Example usage:

class MyClass:
    def __init__(self, attribute1, attribute2):
        self.attribute1 = attribute1
        self.attribute2 = attribute2

    @untyped({"arg1": "attribute1", "arg2": "attribute2"})
    def foo(self, arg1, arg2=None):
        return arg1 + arg2

    @untyped(["attribute1","attribute2"])
    def foo2(self, attribute1, attribute2):
        return attribute1 - attribute2

    @untyped(["attribute1"])
    def foo3(self, attribute1, attribute2=13):
        return attribute1*attribute2


if __name__ == "__main__":
    c = MyClass(1,2)
    #print(c.foo(5))       # 6 #unsupported

    print(f"current signature: {inspect.signature(c.foo)}")  # should now print: (self, arg1, arg2)

    print(f"foo with 2 parameters (mapped): {c.foo(5, 5)} == 10")    # 10 Works!
    print(f"foo with 2 parameters (listed): {c.foo2(5, 5)} == 0")    # 0 Works!
    print(f"foo with 1 self and 1 specified parameter (mapped): {c.foo(arg2=15)} == 16") # 16
    print(f"foo with 1 self and 1 specified parameter (listed): {c.foo2(attribute2=15)} == -14") # -14
    print(f"foo with 2 parameters, called statically (mapped): {MyClass.foo(10, 10)} == 20") # 20
    print(f"foo with 2 parameters, called statically (listed): {MyClass.foo2(10, 10)} == 0") # 0
    print(f"foo with 1 self'd parameter and 1 default parameter (listed): {c.foo3()} == 13")
    print(f"foo with 1 parameter and 1 default parameter (listed), called statically: {MyClass.foo3(2)} == 26")
