from functools import wraps
import inspect
from dataclasses import dataclass

class OptionalParenthesesDecorator:
    def __init__(self, func=None, *args, **kwargs):
        self.func = func
        self.decorator_args = args if args and len(args) > 0 else tuple()
        self.decorator_kwargs = kwargs if len(kwargs) > 0 else dict()
        self.flags = {'was_called_with_parentheses' : False}

    def __call__(self, *args, **kwargs):
        if not callable(self.func):
            # Decorator used with parentheses. reformat like would expect to retrieve without parentheses.
            
            if self.func is not None:
                self.decorator_args = self.decorator_args + tuple([self.func])
            self.func = args[0]
            if not callable(self.func):
                raise TypeError(f'{self.__class__.__name__} can only be applied to callables')
            
            self.flags['was_called_with_parentheses'] = True

            self.user_init()
            self.user_call()

            return self.wrapper
        
        self.user_init()
        self.user_call()

        # Used without parentheses
        return self.wrapper()
    
    def user_init(self):
        pass
    
    def user_call(self):
        pass

    def wrapper(self, *func_args, **func_kwargs):
        # Must call func and return
        result = self.func(*func_args, **func_kwargs)
        return result

class StaticOrInstanceDecorator(OptionalParenthesesDecorator):
    def __init__(self, func=None, *args, **kwargs):
        super().__init__(func, *args, **kwargs)
        self.flags['is_instance_call'] = None
        self.instance = None
        self.owner = None

    class get_exposer:
        def __init__(self, get_endpoint_callable):
            self.get_endpoint = get_endpoint_callable
        
        def __get__(self, instance, owner):
            return self.get_endpoint(instance, owner)
    
    def get_endpoint(self, instance, owner):
        self.flags['is_instance_call'] = instance is not None
        self.instance = instance
        self.owner = owner

        self.user_init()
        self.user_call()
        self.modify_meta()
        self.apply_meta_changes()

        @wraps(self.func)
        def bound_wrapper(*args, **kwargs):
            """ not needed, as get_endpoint always called via get
            if instance:
                print(f'instance: {instance}')
                return self.wrapper(instance, *args, **kwargs)
            else:
                return self.wrapper(*args, **kwargs)
            """
            return self.wrapper(*args, **kwargs)

        return bound_wrapper
    
    def __get__(self, instance, owner):
        return self.get_endpoint(instance, owner)

    def __call__(self, *args, **kwargs):
        
        if not callable(self.func):
            if self.func is not None:
                self.decorator_args = self.decorator_args + tuple([self.func])
            self.func = args[0]
            if not callable(self.func):
                raise TypeError(f'{self.__class__.__name__} can only be applied to callables')
            self.flags['was_called_with_parentheses'] = True
            
            # force __get__ to be called (which will return the wrapper instead)
            return self.get_exposer(self.get_endpoint) #could do just return self, but this is more verbose
        
        self.user_init()
        self.user_call()
        self.modify_meta()
        self.apply_meta_changes()
        
        return self.call_process(args, kwargs)

    def call_process(self, *args, **kwargs):
        return self.wrapper()

    def modify_meta(self):
        pass
    def apply_meta_changes(self):
        pass


@dataclass
class MetaModifyingDecorator(StaticOrInstanceDecorator):
    def __init__(self, func=None, *args, **kwargs):
        super().__init__(func, *args, **kwargs)
        self.meta = {}
        
    def modify_meta(self):
        #override this and set keypairs of self.meta
        #self.meta['foo'] = 'bar'
        pass
    
    @property
    def func_signature(self):
        if '_func_signature' not in self.__dict__:
            self._func_signature = inspect.signature(self.func)
        return self._func_signature
        
    def apply_meta_changes(self):
        for key, value in self.meta.items():
            if key == '__signature__':
                self.func_signature
            setattr(self.func, key, value)

'''
    def __call__(self, *args, **kwargs):
        w = super().__call__(*args, **kwargs)
        self.apply_meta_changes()
        
        return w
'''
class EasyDecorator(MetaModifyingDecorator):
    def modify_meta(self):
        """
        modify function metadata here with the self.meta dictionary. treat this similarly to self.func.__dict__. 
        this is called in init, so does not have access to func_args, etc. 
        has access to the same attributes as wrapper(), except func_args and func_kwargs

        example:
        self.meta['__signature__'] = inspect.Signature([inspect.Parameter('fish', inspect.Parameter.POSITIONAL_OR_KEYWORD)])
        """

    def user_init(self):
        """
        override this init to access all needed self variables
        override original init if you dont need access to all vars
        """
        pass

    def user_call(self):
        """
        same as above
        """
        pass

    def wrapper(self, *func_args, **func_kwargs):
        """
        this is the wrapper you want to override in your inheriting class. you have access to the following attributes:
        - func_args: the arguments given to the function
        - func_kwargs: the keyword arguments given to the function
        - self.decorator_args: args passed to decorator
        - self.decorator_kwargs: kwargs passed to decorator
        - self.flags['was_called_with_parentheses']: True if decorator defined like @CoolDecorator(), False if like @CoolDecorator
        - self.flags['is_instance_call']: True if function called statically (instance passed to function __get__ is None), false if not
        - self.func_signature: orignal func signature, before modifications
        - self.instance = instance of function (returns 'self')
        - self.owner = owner of function (returns class)

        this function should run self.func(*func_args, **func_kwargs) and return the results
        """

        return self.func(*func_args, **func_kwargs)
