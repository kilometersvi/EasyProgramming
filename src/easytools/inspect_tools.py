import inspect

def get_positional_params(func, exclude_self=True):
    if not isinstance(func, inspect.Signature):
        signature = inspect.signature(func)
    else:
        signature = func
    return [
        k
        for k, v in list(signature.parameters.items())[exclude_self:]
        if v.default is inspect.Parameter.empty
    ]

def get_default_kwargs(func):
    if not isinstance(func, inspect.Signature):
        signature = inspect.signature(func)
    else:
        signature = func
    
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }

def has_kwargs(func):
    if not isinstance(func, inspect.Signature):
        signature = inspect.signature(func)
    else:
        signature = func
    
    for param in signature.parameters.values():
        if param.kind == param.VAR_KEYWORD:
            return True
    return False
