
from typing import Generic, TypeVar


class GlslArrayProxy:
    def __init__(self, name):
        self.name = name
        self._id = 0

    def set(self, x):
        pass

    def get(self):
        pass


_Attribute_types = TypeVar("_Attribute_types")


class Attribute(Generic[_Attribute_types]):
    def __init__(self, _type=None, index=0):  # think of better name that dosnt shadow biltin or in
        self.type = _type
        self.index = index
        self.name = ""
        self._id = None

    def set_index(self, index):
        self.index = index

    def set(self, name):
        self.name = name
        return self


IN = "in"
OUT = "out"
INOUT = "inout"
GLOBAL = "global"
AUTO = "auto"

_GlslVariable_types = TypeVar("_GlslVariable_types")


class GlslVariable(Generic[_GlslVariable_types]):
    def __init__(self, _type=None, piping=AUTO):
        self.type = _type
        self.inout = piping
        self.name = ""

    def set(self, name):
        self.name = name
        return self


class Constant:  # todo
    def __init__(self, value, _type=None):
        self.value = value
        self.type = _type
        self.name = ""


_Uniform_types = TypeVar("_Uniform_types")


class Uniform(Generic[_Uniform_types]):
    def __init__(self, _type=None, value=None):  # think of better name that dosnt shadow biltin or in
        self.value = value
        self.type = _type
        self.name = ""

    def set(self, name):
        self.name = name
        return self

    def set_type(self, t):
        self.type = t


class GlslFuntion:
    def __init__(self, f, shader="all"):
        self.shader = [shader]
        self.callback = f
        self.glsl = ""

    def __call__(self, *args, **kwargs):
        return self.callback(*args, **kwargs)

