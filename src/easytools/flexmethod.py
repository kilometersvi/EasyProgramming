from functools import wraps, update_wrapper
import inspect
import textwrap
from easytools.inspect_tools import has_var_keyword, get_positional_params, get_default_kwargs, get_var_params
from typing import Dict, Tuple, Union, List, Any, Callable, Type, Literal, Optional
from easytools.decorator_bases import EasyDecorator
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)

class ArgumentParser:

    _for: Literal['static', 'instance', 'static or instance', ''] = ''
    
    def __init__(self, func, static_params, static_defaults, func_params, func_defaults, func_vars, default_signature=None):
        self.func = func
        self.static_params = static_params
        self.static_defaults = static_defaults
        self.func_params = func_params if 'static' not in self._for else func_params[1:]
        self.func_defaults = func_defaults
        self.func_vars = func_vars
        self.default_signature = default_signature
        self.n_p = None if 'static' not in self._for else func_params[0]+'_'

        self.instance_signature = self.create_instance_signature()
        self.static_signature = self.create_static_signature()

        self.error_check()
    
    @classmethod
    def condition_check(cls, decorator_args, decorator_kwargs, func_params, func_defaults) -> bool:
        return False

    def __call__(self, args, kwargs) -> Tuple[Union[Dict,Any], List, Dict[str,Any]]:
        raise NotImplementedError()
    
    def create_instance_signature(self) -> inspect.Signature:
        if self.default_signature:
            return self.default_signature
        return inspect.signature(self.func)

    def create_static_signature(self) -> inspect.Signature:
        if self.default_signature:
            return self.default_signature
        return inspect.signature(self.func)
    
    def error_check(self):
        return True
    
    def _param_mod(self, p):
        if p[:len(self.n_p)] == self.n_p:
            return p
        return self.n_p + p
    
    @classmethod
    def pattern_match_failure(cls, decorator_args, decorator_kwargs, func_params, func_defaults):
        raise ValueError()
    
class DummyParser(ArgumentParser):
    """
    Dummy Insert Mode

    If no arguments are configured in the decorator, treat this decorator
        as a specifier telling to user to pass a dictionary or namespace object
        as argument 0 where self would be passed
    """
    
    _for = 'static'

    def __call__(self, args, kwargs): 

        return args[0], args[1:], kwargs
    
    @classmethod
    def condition_check(cls, decorator_args, decorator_kwargs, func_params, func_defaults):
        #implies decorator args & kwargs contains static args & kwargs
        implemented_keys = list(decorator_args) + list(decorator_kwargs.keys())
        required_keys = list(func_params[1:]) + list(func_defaults.keys())

        return len(implemented_keys) == 0

    @classmethod
    def pattern_match_failure(cls, decorator_args, decorator_kwargs, func_params, func_defaults):
        raise ValueError('Too many arguments.')

class ArgAttrMapParser(ArgumentParser):
    """
    Attr-Arg Map Mode

    Map attributes in instance to locals attributes, such that the 'self'
        keyword is not used in the instance function. Useful for converting 
        static functions to instance functions.

        # not implemented. todo: find a way to fit adaptive_method into this; don't know how to determine
        # if this behavior was intended by decorator args and kwargs when they are treated as a signature.
        # all other methods have some condition to determine if intended.
    """
    pass

class SignatureInjectParser(ArgumentParser):
    """
    Inject Namespace Into Signature Mode

    If not all parameters from function signature are defined in decorator's arguments and
        keyword arguments, the decorator args are used to define the parameters that will be 
        accessible through the namespace. Namespace positional parameters will be placed in the front
        of the existing func parameters. For example, in the following:
        ```
        MyClass:
            @flexmethod('arg0')
            def foo(nself, arg1):
                return nself.arg0 + arg1
        ```
        The function signature when called statically will be: arg0, arg1; as such, the function can be
        called with `MyClass.foo(arg0=0,arg1=0)' or with 'InstanceOfClass.foo(arg1=0) (keyword arguments
        used illustratively, both positional and keyword arguments supported like in normal python function)'
    """

    _for = 'static'

    def error_check(self):
        # check for clashing keys when in inject mode (when key is not positional but parametrized in both nmsp and func, 
        # cannot determine if user passed to be intended to be used for nmsp or func)
        for k, v in self.static_defaults.items():
            if k in self.func_defaults:
                logging.info(self.func_defaults)
                logging.info(self.func_params)
                logging.info(self.static_defaults)
                conflictmsg = " ".join(textwrap.dedent("""
                    The keyword '{k}' is specified as both a parameter and a namespace attribute, leading to ambiguity.
                    Please rename the parameter to '{nmsp_p}{k}' to ensure clarity and avoid conflicts when injecting
                    namespace attributes into the signature.
                """).split())
                raise ValueError(conflictmsg.format(k=k, nmsp_p=self.n_p))
        
        return True
    
    @classmethod
    def condition_check(cls, decorator_args, decorator_kwargs, func_params, func_defaults):
        #implies decorator args & kwargs contains static args & kwargs
        implemented_keys = list(decorator_args) + list(decorator_kwargs.keys())
        required_keys = list(func_params[1:]) + list(func_defaults.keys())

        return not all(k in implemented_keys for k in required_keys)  
        
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
                #logging.info(f'[ksort] {k} in self.func_params')
                new_kwargs[k] = v
            elif k in self.static_params:
                #logging.info(f'[ksort] {k} in self.static_params')
                nmsp_dict[k] = v
            elif k in self.static_defaults:
                #logging.info(f'[ksort] {k} in self.static_defaults')
                nmsp_dict[k] = v
            elif k in self.func_defaults:
                #logging.info(f'[ksort] {k} in self.func_defaults')
                new_kwargs[k] = v
            elif k[:len(self.n_p)] == self.n_p:
                #logging.info(f'[ksort] {k} has prefix {self.n_p}')
                nmsp_dict[k[len(self.n_p):]] = v
            elif has_var_keyword(self.static_signature):
                #if func has ** term, lets put this kw in there
                new_kwargs[k] = v

            else:
                """
                logging.info(f'[ksort] {k} unsorted; must belong to self')
                nmsp_dict[k] = v
                """
                #this must be a user error; if there is an attribute in self that is required for computation,
                # it should be listed in namespace parameters. technically nothing wrong with this,
                # however...

                conflictmsg = " ".join(textwrap.dedent(f"""
                    {self.func.__name__}() got an unexpected keyword argument {k}. If this keyword argument was meant 
                    to be assigned to the namespace, include it in the decorator with a default value, or change the 
                    key to '{self.n_p}{k}'. When using \033[1m{'flexmethod'}\033[0m, __init__() is not called when 
                    creating dummy instances. {self.static_signature}
                """).split())
                raise TypeError(conflictmsg)
        
        logging.info('at call:')
        logging.info(self.func_defaults)
        logging.info(self.func_params)
        logging.info(self.static_defaults)
                
        logging.info(f"nmsp_dict new: {nmsp_dict}")
        logging.info(f"new args: {new_args}")
        logging.info(f"new kwargs: {new_kwargs}")

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
        
        if self.func_vars[0]:
            parameters.append(inspect.Parameter(self.func_vars[0], inspect.Parameter.VAR_POSITIONAL))

        # Add keyword parameters with defaults
        for name, default in self.static_defaults.items():
            name = self._param_mod(name)
            param = inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD, default=default)
            parameters.append(param)
        
        for name, default in self.func_defaults.items():
            param = inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD, default=default)
            parameters.append(param)

        if self.func_vars[1]:
            parameters.append(inspect.Parameter(self.func_vars[1], inspect.Parameter.VAR_KEYWORD))


        return inspect.Signature(parameters)
   
class FullSignatureParser(ArgumentParser):

    """
    Full Static Signature Mode

    If all parameters in function signature are defined in decorator's arguments 
        and keyword arguments, treat the decorator args as an alternate signature for the function,
        used whenever the function is called statically
    """
    
    _for = 'static'

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
        

        #logging.info(f"nmsp_attrs new: {nmsp_attrs}")
        #logging.info(f"new args: {()}")
        #logging.info(f"new kwargs: {new_kwargs}")

        return nmsp_attrs, [], new_kwargs
    
    @classmethod
    def condition_check(cls, decorator_args, decorator_kwargs, func_params, func_defaults):
        #implies decorator args & kwargs contains static args & kwargs
        implemented_keys = list(decorator_args) + list(decorator_kwargs.keys())
        required_keys = list(func_params[1:]) + list(func_defaults.keys())

        return all(k in implemented_keys for k in required_keys)
    
    def create_static_signature(self):
        # create static signature
        parameters = []
        
        # Add positional parameters
        for name in self.static_params:
            if name not in self.func_defaults.keys() and name not in self.func_params:
                name = self._param_mod(name)
            param = inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            parameters.append(param)
        
        # Add var parameter if present
        if self.func_vars[0]:
            parameters.append(inspect.Parameter(self.func_vars[0], inspect.Parameter.VAR_POSITIONAL))

        # Add keyword parameters with defaults
        for name, default in self.static_defaults.items():
            if name not in self.func_defaults.keys() and name not in self.func_params:
                name = self._param_mod(name)
            param = inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD, default=default)
            parameters.append(param)
        
        # Add var kwarg if present
        if self.func_vars[1]:
            parameters.append(inspect.Parameter(self.func_vars[1], inspect.Parameter.VAR_KEYWORD))


        return inspect.Signature(parameters)
    
    @classmethod
    def pattern_match_failure(cls, decorator_args, decorator_kwargs, func_params, func_defaults):
        implemented_keys = list(decorator_args) + list(decorator_kwargs.keys())
        required_keys = list(func_params[1:]) + list(func_defaults.keys())

        v = [k not in implemented_keys for k in required_keys]

        raise ValueError(f'Incomplete signature; missing parameter(s) {",".join(v)} from static signature')


class ArgumentParsingDecorator(EasyDecorator):

    def set_parsers(self):
        #override with list of parsers
        self.parsers = None
    
    def user_init(self):
        
        logging.info('initing')

        self.func_params = get_positional_params(self.func_signature, exclude_self=False) 
        self.func_defaults = get_default_kwargs(self.func_signature)
        self.func_vars = get_var_params(self.func_signature)
        
        logging.info(f'func defaults: {self.func_defaults}')
        logging.info(f'self.func_signature: {self.func_signature}')
        self.set_parsers()

        #determine handling mode
        self.prepare_args = None

        for parser in self.parsers:
            if parser.condition_check(self.decorator_args, self.decorator_kwargs, self.func_params, self.func_defaults): 
                logging.info(f'parser found: {parser}, created with:')
                logging.info(self.decorator_args)
                logging.info(self.decorator_kwargs)
                logging.info(self.func_params)
                logging.info(self.func_defaults)
                self.prepare_args = parser(self.func, self.decorator_args, self.decorator_kwargs, self.func_params, self.func_defaults, self.func_vars, self.func_signature)
                break
        
        if self.prepare_args is None:
            if len(self.parsers) == 1:
                self.parsers[0].pattern_match_failure(self.decorator_args, self.decorator_kwargs, self.func_params, self.func_defaults)
            elif len(self.parsers) > 1:
                raise ValueError(f"Decorator arguments are not sufficient. Ensure all required parameters are implemented.")
            else:
                raise NotImplementedError('flexmethod method not implemented.')

        if self.prepare_args._for == 'static':
            self.static_init()
        else:
            self.inst_init()
        
        # update signature
        self.static_signature = self.prepare_args.static_signature
        self.instance_signature = self.prepare_args.instance_signature
        
        
    def static_init(self):
        #in static call, decorator args & decorator kwargs = static args & static kwargs
        self.static_params = self.decorator_args
        self.static_defaults = self.decorator_kwargs

        #namespace prefix; explicitly define param to belong to namespace
        self.n_p = self.func_params[0]+'_'

        #general implementation error checks

        # check that user did not specify duplicate parameters
        duplicate_keys = set(self.static_params) & set(self.static_defaults.keys())
        if duplicate_keys:
            raise ValueError(f"Duplicate parameters implemented: {', '.join(duplicate_keys)}")
        if len(self.static_params) != len(set(self.static_params)):
            raise ValueError(f"Duplicate parameters implemented: {', '.join([k for k in self.static_params if self.static_params.count(k) > 1])}")
        if len(self.static_defaults.keys()) != len(set(self.static_defaults.keys())):
            raise ValueError(f"Duplicate parameters implemented: {', '.join([k for k in self.static_defaults if list(self.static_defaults.keys()).count(k) > 1])}")
    
    def inst_init(self):
        pass
    
    def wrapper(self, *args, **kwargs):
        
        logging.info("wrapper called")
        #default wrapper for this class is meant for static, override for inst
        logging.info(self.__dict__)

        if self.flags['is_instance_call']:
            #instance call just calls function in default wrapper
            
            logging.info(args)
            logging.info(kwargs)
            self.instance.__dict__.update({'__static_from_flexmethod__': False})
            return self.func(self.instance, *args, **kwargs)
        
        #otherwise is static call
        nmsp_attrs, new_args, new_kwargs = self.prepare_args(args, kwargs)
        logging.info('passed')

        #returned dict representing nself namespace
        if isinstance(nmsp_attrs, dict):
            logging.info('was instance called')
            # remove nmsp tags
            to_proc = []
            for k, v in nmsp_attrs.items():
                if len(k) > len(self.n_p) and k[:len(self.n_p)] == self.n_p:
                    to_proc.append(k)
            
            for k in to_proc:
                nmsp_attrs[k[len(self.n_p):]] = nmsp_attrs[k]
                del nmsp_attrs[k]
            
            # attribute allowing function to determine if it was called statically or not
            nmsp_attrs['__static_from_flexmethod__'] = True

            # make dummy instance that will act as nself namespace
            nself = self.owner.__new__(self.owner)
            nself.__dict__.update(nmsp_attrs)

            return self.func(nself, *new_args, **new_kwargs)
        
        # arg preparer returned the nself namespace
        else:
            nmsp_attrs.__dict__.update({'__static_from_flexmethod__': True})

            nself = nmsp_attrs
        
        return self.func(nself, *new_args, **new_kwargs)
    
    def modify_meta(self):
        if not self.flags['is_instance_call'] and self.prepare_args._for == 'static':
            self.meta['__signature__'] = self.static_signature
        
        elif self.flags['is_instance_call'] and self.prepare_args._for == 'instance':
            self.meta['__signature__'] = self.instance_signature
            
    def call_process(self, *args, **kwargs):

        logging.info('called')
        # static call
        if self.instance is None:
            # used for static case
            if self.prepare_args._for == 'static':
                return self.wrapper()
            
            # not used for static case; return method as is
            else:
                return self.func

        # instance call
        else:
            if self.prepare_args._for == 'instance':
                return self.wrapper()

            # not used for instance case; return the method as is
            else:
                return self.func


class flexmethod(ArgumentParsingDecorator):

    # Default call uses parent wrapper, eg @flexmethod
    # Uses pattern matching to determine between the three instance-to-static parse modes
    def set_parsers(self):
        if self.flags['was_called_with_parentheses']:
            self.parsers = [DummyParser, FullSignatureParser, SignatureInjectParser]
        else:
            self.parsers = [DummyParser]

    # Namespace Insert Mode
    class nsinsert(ArgumentParsingDecorator):
        # No arguments; signifies that the function, when called statically, can take parameter in the place of self, which is a namespace
        # Convert instance method code to be callable statically (instance to static)
        # Call with @flexmethod.nsinsert or @flexmethod.nsinsert()

        def set_parsers(self):
            self.parsers = [DummyParser]

    # Namespace Signature Sync Mode
    class nssync(ArgumentParsingDecorator):
        # Accepts parameters to be inserted into signature, which will be in the scope of the nself namespace
        # New function signature, when called statically, will be the gathered form of (*decorator_args, *func_args, **func_kwargs, **decorator_kwargs)
        # Convert instance method code to be callable statically (instance to static)
        # Call with @flexmethod.nssync(*attrs, **attrs_with_defaults)

        def set_parsers(self):
            if self.flags['was_called_with_parentheses']: 
                self.parsers = [SignatureInjectParser]
            else:
                raise SyntaxError('flexmethod.nssync missing parenthesis.')
    
    # Alternate Signature Mode
    class staticsig(ArgumentParsingDecorator):
        # Accepts full alternate signature for when the function is called statically
        # New function signature, when called statically, will be the gathered form of (*decorator_args, **decorator_kwargs)
        # Convert instance method code to be callable statically (instance to static)
        # Call with @flexmethod.staticsig

        def set_parsers(self):
            if self.flags['was_called_with_parentheses']: 
                self.parsers = [FullSignatureParser]
            else:
                raise SyntaxError('flexmethod.staticsig missing parenthesis.')

    # Parameter-Self Bind Mode
    class parambind(ArgumentParsingDecorator):
        # Accepts mapping of attributes to function parameters
        # Call function with instance, where attributes in instance are passed to the function's arguments by parameter name according to mapping
        # Convert static method code to be callable in instance (static to instance)
        # Call with @flexmethod.parambind
        pass
    