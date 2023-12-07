import inspect

def get_sig_if_not_sig(f_or_s):
    if not isinstance(f_or_s, inspect.Signature):
        if callable(f_or_s):
            return inspect.signature(f_or_s)
        raise TypeError("Function not callable; has no signature")
    else:
        return f_or_s
    
def get_positional_params(func_or_sig, exclude_self=True):
    signature = get_sig_if_not_sig(func_or_sig)
    return [
        k
        for k, v in list(signature.parameters.items())[exclude_self:]
        if v.default is inspect.Parameter.empty and v.kind is not inspect.Parameter.VAR_POSITIONAL and v.kind is not inspect.Parameter.VAR_KEYWORD
    ]

def get_default_kwargs(func_or_sig):
    signature = get_sig_if_not_sig(func_or_sig)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty and v.kind is not inspect.Parameter.VAR_KEYWORD
    }

def has_kwargs(func_or_sig):
    signature = get_sig_if_not_sig(func_or_sig)
    for param in signature.parameters.values():
        if param.kind == param.VAR_KEYWORD:
            return True
    return False

def has_var_positional(func_or_sig):
    signature = get_sig_if_not_sig(func_or_sig)
    params = signature.parameters.values()
    return any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in params)

def has_var_keyword(func_or_sig):
    signature = get_sig_if_not_sig(func_or_sig)
    params = signature.parameters.values()
    return any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params)

def get_var_params(func_or_sig):
    signature = get_sig_if_not_sig(func_or_sig)
    params = signature.parameters.values()
    var_pos = [p for p in params if p.kind == inspect.Parameter.VAR_POSITIONAL]
    var_kw = [p for p in params if p.kind == inspect.Parameter.VAR_KEYWORD]
    
    return (var_pos[0].name if len(var_pos) == 1 else None, var_kw[0].name if len(var_kw) == 1 else None)
