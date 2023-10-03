from mutables import MutableInteger
import inspect

class adjumerate:
    def __init__(self, iterable, start=0):
        self._iterable = iterable
        self._start = start

    def __iter__(self):
        return Counter(self._iterable, init_value=self._start)


class Counter:
    def __init__(self, iterable, init_value=0):
        self._iterable = iter(iterable)
        self._count = CountObject(init_value)

    def __iter__(self):
        return self

    def __next__(self):
        value = next(self._iterable)
        result = (self._count, value)
        self._count.value += 1
        self._count.raw += 1
        return result

    @property
    def count(self):
        return self._count.value

    @count.setter
    def count(self, value):
        self._count.value = value


class CountObject(MutableInteger):
    def __init__(self, value=0):
        super().__init__(value-1)
        self.raw = -1

    def unmodified_count(self):
        return self.raw

    def __setattr__(self, name, value):
        # Get the caller frame
        caller_frame = inspect.currentframe().f_back
        caller_name = caller_frame.f_code.co_name
        caller_instance = caller_frame.f_locals.get("self")

        # Enforce conditions for `raw` attribute
        if name == "raw":
            if caller_name == "__init__" and (caller_instance is not None and isinstance(caller_instance, CountObject)):
                pass
            elif caller_name != "__next__" or (caller_instance is not None and not isinstance(caller_instance, Counter)):
                raise AttributeError("Cannot modify `raw` outside the `__next__` method of the `Counter` class!")

        # Allow other attributes to be set normally
        super(CountObject, self).__setattr__(name, value)



if __name__ == "__main__":

    #for i, x in enumerate(range(10)):
    #    print(i, x)

    """
    for i, x in CustomEnumerator(range(10)):
        print(i.unmodified_count(), i, x)

        if i == 5:
            i.set(0)  # Adjust the counter directly

        if i.unmodified_count() == 9:
            print(f"sum: {7 + i}")
            print(type(i))
            i.raw += 1
            print(i.unmodified_count())

    """
    for i, x in CustomEnumerator(range(10)):
        print(i)
        print(i)
