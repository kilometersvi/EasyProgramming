class MutableInteger:

    def __init__(self, value=0):
        self._value = value

    def __repr__(self):
        return int(self._value)

    def __str__(self):
        return str(int(self._value))

    def __int__(self):
        return int(self._value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = int(new_value)

    def set(self, value):
        if isinstance(value, int):
            self._value = value
        else:
            raise ValueError("MutableInteger value must be an integer")

    def __iadd__(self, value):
        if isinstance(other, int):
            self._value += other
            return self
        raise ValueError("Can only add integers to MutableInteger")

    def __isub__(self, other):
        if isinstance(other, int):
            self._value -= other
            return self
        raise ValueError("Can only subtract integers to MutableInteger")

    # Arithmetic methods:
    def __add__(self, other):
        return int(self).__add__(other)

    def __sub__(self, other):
        return int(self).__sub__(other)

    def __mul__(self, other):
        return int(self).__mul__(other)

    def __truediv__(self, other):
        return int(self).__truediv__(other)

    def __floordiv__(self, other):
        return int(self).__floordiv__(other)

    def __mod__(self, other):
        return int(self).__mod__(other)

    def __pow__(self, power, modulo=None):
        if modulo is None:
            return int(self).__pow__(power)
        return int(self).__pow__(power, modulo)

    # Bitwise operations:

    def __lshift__(self, other):
        return int(self).__lshift__(other)

    def __rshift__(self, other):
        return int(self).__rshift__(other)

    def __and__(self, other):
        return int(self).__and__(other)

    def __xor__(self, other):
        return int(self).__xor__(other)

    def __or__(self, other):
        return int(self).__or__(other)

    # Reverse arithmetic methods for operations where `MutableInteger` is the right operand:

    def __radd__(self, other):
        return other + int(self)

    def __rsub__(self, other):
        return other - int(self)

    def __rmul__(self, other):
        return other * int(self)

    def __rtruediv__(self, other):
        return other / int(self)

    def __rfloordiv__(self, other):
        return other // int(self)

    def __rmod__(self, other):
        return other % int(self)

    def __rpow__(self, base):
        return base ** int(self)

    def __rlshift__(self, other):
        return other << int(self)

    def __rrshift__(self, other):
        return other >> int(self)

    def __rand__(self, other):
        return other & int(self)

    def __rxor__(self, other):
        return other ^ int(self)

    def __ror__(self, other):
        return other | int(self)

    # Comparison methods:

    def __lt__(self, other):
        return int(self).__lt__(other)

    def __le__(self, other):
        return int(self).__le__(other)

    def __eq__(self, other):
        return int(self).__eq__(other)

    def __ne__(self, other):
        return int(self).__ne__(other)

    def __gt__(self, other):
        return int(self).__gt__(other)

    def __ge__(self, other):
        return int(self).__ge__(other)

    # Conversion methods:

    def __float__(self):
        return float(self._value)

    def __complex__(self):
        return complex(self._value)

    def __bool__(self):
        return bool(self._value)

    def __str__(self):
        return str(self._value)

    # Bitwise unary:

    def __invert__(self):
        return ~self._value

    # Additional functionalities:

    def __hash__(self):
        return hash(self._value)

    def __round__(self, n=None):
        return round(self._value, n)

    def __divmod__(self, other):
        return divmod(self._value, other)

    def __index__(self):
        return int(self)
