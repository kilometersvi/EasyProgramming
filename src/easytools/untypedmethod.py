from functools import wraps, update_wrapper
import inspect
import textwrap
from easytools.inspect_tools import get_positional_params, get_default_kwargs, has_kwargs
from typing import Dict, Tuple, Union, List, Any


class ArgumentParser:
    def __init__(self, func, static_params, static_defaults, func_params, func_defaults, nmsp_prefix):
        self.func = func
        self.static_params = static_params
        self.static_defaults = static_defaults
        self.func_params = func_params[1:]
        self.func_defaults = func_defaults
        self.n_p = nmsp_prefix

        self.instance_signature = inspect.signature(func)
        self.static_signature = self.create_static_signature()

    def __call__(self, args, kwargs) -> Tuple[Union[Dict,Any], List, Dict[str,Any]]:
        raise NotImplementedError()
    
    def create_static_signature(self) -> inspect.Signature:
        raise NotImplementedError()
    
    def _param_mod(self, p):
        if p[:len(self.n_p)] == self.n_p:
            return p
        return self.n_p + p
    

class DummyParser(ArgumentParser):
    def __call__(self, args, kwargs):
        
        return args[0], args[1:], kwargs
    
    def create_static_signature(self):
        # create static signature

        return self.instance_signature

        

class ArgAttrMapParser(ArgumentParser):
    pass

class SignatureInjectParser(ArgumentParser):
    def __init__(self, func, static_params, static_defaults, func_params, func_defaults, nmsp_prefix):
        super().__init__(func, static_params, static_defaults, func_params, func_defaults, nmsp_prefix)

        # check for clashing keys when in inject mode (when key is not positional but parametrized in both nmsp and func, 
        # cannot determine if user passed to be intended to be used for nmsp or func)
        for k, v in static_defaults.items():
            if k in func_defaults:
                conflictmsg = " ".join(textwrap.dedent("""
                    The keyword '{k}' is specified as both a parameter and a namespace attribute, leading to ambiguity.
                    Please rename the parameter to '{nmsp_p}{k}' to ensure clarity and avoid conflicts when injecting
                    namespace attributes into the signature.
                """).split())
                raise ValueError(conflictmsg.format(k=k, nmsp_p=self.n_p))
        
    def __call__(self, args, kwargs):
        # create a dummy instance with the provided nmsp_attrs
        
        # divide args into func args and namespace attributes
        idx = len(self.static_params)
        nmsp_dict = dict(zip(self.static_params, args[:idx]))
        idx = len(nmsp_dict)
        nmsp_dict.update(self.static_defaults)

        new_args = args[idx:]
        

        # filter and map to function kwargs or to namespace attrs

        new_kwargs = {}
        for k, v in kwargs.items():
            if k in self.func_params:
                #print(f'[ksort] {k} in self.func_params')
                new_kwargs[k] = v
            elif k in self.static_params:
                #print(f'[ksort] {k} in self.static_params')
                nmsp_dict[k] = v
            elif k in self.static_defaults:
                #print(f'[ksort] {k} in self.static_defaults')
                nmsp_dict[k] = v
            elif k in self.func_defaults:
                #print(f'[ksort] {k} in self.func_defaults')
                new_kwargs[k] = v
            elif k[:len(self.n_p)] == self.n_p:
                #print(f'[ksort] {k} has prefix {self.n_p}')
                nmsp_dict = k
            elif has_kwargs(self.instance_signature):
                #print(f'[ksort] func has kwargs, so lets put it in there')
                new_kwargs[k] = v
            else:
                new_kwargs[k] = v
                """
                print(f'[ksort] {k} unsorted; must belong to self')
                nmsp_dict[k] = v
                """
                #this must be a user error; if there is an attribute in self that is required for computation,
                # it should be listed in namespace parameters
                conflictmsg = " ".join(textwrap.dedent(f"""
                    {self.func.__name__}() got an unexpected keyword argument {k}. If this keyword argument was meant 
                    to be assigned to the namespace, include it in the decorator with a default value, or change the 
                    key to '{self.n_p}{k}'. When using \033[1m{untypedmethod}\033[0m, __init__() is not called when 
                    creating dummy instances.
                """).split())
                raise TypeError(conflictmsg)
        
        #print(f"nmsp_dict new: {nmsp_dict}")
        #print(f"new args: {new_args}")
        #print(f"new kwargs: {new_kwargs}")

        return nmsp_dict, new_args, new_kwargs
    
    def create_static_signature(self):

        # create static signature
        parameters = []

        # Add positional parameters
        for name in self.static_params:
            name = self._param_mod(name)
            param = inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            parameters.append(param)
        
        for name in self.func_params:
            param = inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            parameters.append(param)

        # Add keyword parameters with defaults
        for name, default in self.static_defaults.items():
            name = self._param_mod(name)
            param = inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD, default=default)
            parameters.append(param)
        
        for name, default in self.func_defaults.items():
            param = inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD, default=default)
            parameters.append(param)

        return inspect.Signature(parameters)
    
class FullSignatureParser(ArgumentParser):
    def __call__(self, args, kwargs):
        # full static signature defined in decorator args

        new_kwargs = {}
        nmsp_attrs = {}
        p = 0

        for k, v in kwargs.items():
            if k in self.func_defaults.keys():
                new_kwargs[k] = v
            elif k in self.func_params:
                new_kwargs[k] = v
                p += 1
            else:
                nmsp_attrs[k] = v
        
        for i, a in enumerate(args):
            if i < len(self.static_params):
                param = self.static_params[i]
            else:
                param = list(self.static_defaults.keys())[i - len(self.static_params)]
            
            if param in self.func_params:
                new_kwargs[param] = a
                p += 1
            else:
                nmsp_attrs[param] = a
        
        if p != len(self.func_params):
            msg = " ".join(textwrap.dedent(f"""
                {self.func.__name__}() expected {len(self.static_params)} 
                argument{'s' if len(self.static_params) > 1 else ''}, got 
                {len(self.static_params) - (len(self.func_params) - p)}
                """).split())
            raise TypeError(msg)

        for k, v in self.static_defaults.items():
            if k not in new_kwargs.keys() and k not in nmsp_attrs.keys():
                if k in self.func_defaults.keys():
                    new_kwargs[k] = v
                else:
                    nmsp_attrs[k] = v
        
        #print(f"nmsp_attrs new: {nmsp_attrs}")
        #print(f"new args: {()}")
        #print(f"new kwargs: {new_kwargs}")

        return nmsp_attrs, [], new_kwargs
    
    def create_static_signature(self):
        # create static signature
        parameters = []
        
        # Add positional parameters
        for name in self.static_params:
            if name not in self.func_defaults.keys() and name not in self.func_params:
                name = self._param_mod(name)
            param = inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            parameters.append(param)

        # Add keyword parameters with defaults
        for name, default in self.static_defaults.items():
            if name not in self.func_defaults.keys() and name not in self.func_params:
                name = self._param_mod(name)
            param = inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD, default=default)
            parameters.append(param)

        return inspect.Signature(parameters)


class SignatureModifiedFunction:
    def __init__(self, func, signature=None):
        update_wrapper(self, func)
        self.func = func
        if signature is None:
            signature = inspect.signature(func)
        self.__signature__ = signature

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
    
    def __get__(self, instance, owner):
        return self.func


def untypedmethod(*args, **kwargs):
    class HandlerFactory:
        def __init__(self, func):
            self.func = func

            func_params = get_positional_params(func, exclude_self=False)
            func_defaults = get_default_kwargs(func) 


            self.static_params = static_params
            self.static_defaults = static_defaults
            self.func_params = func_params
            self.func_defaults = func_defaults

            implemented_keys = list(static_params) + list(static_defaults.keys())
            required_keys = list(func_params[1:]) + list(func_defaults.keys())

            #namespace prefix; explicitly define param to belong to namespace
            self.n_p = func_params[0]+'_'


            # determine handling mode
            if True:
                if len(implemented_keys) == 0:
                    """
                    Dummy Insert Mode

                    If no arguments are configured in the decorator, treat this decorator
                        as a specifier telling to user to pass a dictionary or namespace object
                        as argument 0 where self would be passed
                    """
                    self.prepare_args = DummyParser(self.func, static_params, static_defaults, func_params, func_defaults, self.n_p)
                

                elif False:
                    """
                    Attr-Arg Map Mode

                    Map attributes in instance to locals attributes, such that the 'self'
                        keyword is not used in the instance function. Useful for converting 
                        static functions to instance functions.

                        # not implemented. todo: find a way to fit adaptive_method into this; don't know how to determine
                        # if this behavior was intended by decorator args and kwargs when they are treated as a signature.
                        # all other methods have some condition to determine if intended.
                    """
                    self.prepare_args = ArgAttrMapParser(self.func, static_params, static_defaults, func_params, func_defaults, self.n_p)

                
                elif all(k in implemented_keys for k in required_keys):
                    """
                    Full Static Signature Mode

                    If all parameters in function signature are defined in decorator's arguments 
                        and keyword arguments, treat the decorator args as an alternate signature for the function,
                        used whenever the function is called statically
                    """
                    self.prepare_args = FullSignatureParser(self.func, static_params, static_defaults, func_params, func_defaults, self.n_p)
                

                else:
                    """
                    Inject Namespace Into Signature Mode

                    If not all parameters from function signature are defined in decorator's arguments and
                        keyword arguments, the decorator args are used to define the parameters that will be 
                        accessible through the namespace. Namespace positional parameters will be placed in the front
                        of the existing func parameters. For example, in the following:
                        ```
                        MyClass:
                            @untypedmethod('arg0')
                            def foo(nself, arg1):
                                return nself.arg0 + arg1
                        ```
                        The function signature when called statically will be: arg0, arg1; as such, the function can be
                        called with `MyClass.foo(arg0=0,arg1=0)' or with 'InstanceOfClass.foo(arg1=0) (keyword arguments
                        used illustratively, both positional and keyword arguments supported like in normal python function)'
                    """

                    self.prepare_args = SignatureInjectParser(self.func, static_params, static_defaults, func_params, func_defaults, self.n_p)
            
            # implementation error checks

            # check that user did not specify duplicate parameters
            duplicate_keys = set(static_params) & set(static_defaults.keys())
            if duplicate_keys:
                raise ValueError(f"Duplicate parameters implemented: {', '.join(duplicate_keys)}")
            if len(static_params) != len(set(static_params)):
                raise ValueError(f"Duplicate parameters implemented: {', '.join([k for k in static_params if static_params.count(k) > 1])}")
            if len(static_defaults.keys()) != len(set(static_defaults.keys())):
                raise ValueError(f"Duplicate parameters implemented: {', '.join([k for k in static_defaults if list(static_defaults.keys()).count(k) > 1])}")
            
            # update signature
            self.static_signature = self.prepare_args.static_signature
            self.instance_signature = inspect.signature(self.func)
            

        def __get__(self, instance, owner):

            # static call
            if instance is None:
                @wraps(self.func)
                def wrapper(*args, **kwargs):
                    nmsp_attrs, new_args, new_kwargs = self.prepare_args(args, kwargs)

                    if isinstance(nmsp_attrs, dict):
                        # remove nmsp tags
                        to_proc = []
                        for k, v in nmsp_attrs.items():
                            if len(k) > len(self.n_p) and k[:len(self.n_p)] == self.n_p:
                                to_proc.append(k)
                        
                        for k in to_proc:
                            nmsp_attrs[k[len(self.n_p):]] = nmsp_attrs[k]
                            del nmsp_attrs[k]
                        
                        # make dummy instance that will act as nself namespace
                        nself = owner.__new__(owner)
                        nself.__dict__.update(nmsp_attrs)

                    else:
                        # arg preparer returned the nself namespace
                        nself  = nmsp_attrs
                    
                    return self.func(nself, *new_args, **new_kwargs)
                
                wrapper.__signature__ = self.static_signature

                return wrapper

            # instance call
            else:
                # return the method as is
                return self.func.__get__(instance, owner)
        
    if args and callable(args[0]):
        # decorator used without parentheses
        func = args[0]
        static_params = []
        static_defaults = {}

        return HandlerFactory(func)
    
    else:
        # decorator used with parentheses
        static_params = args
        static_defaults = kwargs

        def decorator(func):
            return HandlerFactory(func)

        return decorator


