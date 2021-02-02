
from OpenGL.GL import *
from OpenGL.GL.shaders import *
import numpy as np


class Vao:
    def __init__(self):
        self._id = glGenVertexArrays(1)
        #self.normalized = False
        self.__vbo = {}

    def __setitem__(self, key, value):
        # test if vbo, ibo...
        self.__vbo[key] = value
        glBindVertexArray(self._id)
        glBindBuffer(GL_ARRAY_BUFFER, value._id)
        glVertexAttribPointer(key, value.dimensions, value.type, value.normalised, 0, ctypes.c_void_p(0))
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def __getitem__(self, item):
        return self.__vbo[item]

    def enable(self, index):
        glBindVertexArray(self._id)
        glEnableVertexAttribArray(index)
        glBindVertexArray(0)

    def disable(self, index):
        glBindVertexArray(self._id)
        glDisableVertexAttribArray(index)
        glBindVertexArray(0)


class Vbo:
    buffert = GL_ARRAY_BUFFER
    _types = {#ints
            np.byte: GL_BYTE,
            np.ubyte: GL_UNSIGNED_BYTE,
            np.short: GL_SHORT,
            np.ushort: GL_UNSIGNED_SHORT,
            np.intc: GL_INT,
            np.uintc: GL_UNSIGNED_INT,
            # floats
            np.float16: GL_HALF_FLOAT,
            np.float32: GL_FLOAT,
            np.float64: GL_DOUBLE

        #GL_FLOAT, GL_DOUBLE, GL_FIXED

              }

    def __init__(self):
        self._id = glGenBuffers(1)
        self.dimensions = None
        self.len = 0
        self.type = GL_INT
        self.normalised = False

    def set_data(self, data: np.array, _type=GL_DYNAMIC_DRAW, dimensions=None):
        size = data.nbytes
        s = data.shape
        self.len = s[0]
        self.type = Vbo._types[data.dtype.type]

        if len(s) > 2:
            raise Exception("invalid array shape")
        if len(s) >= 1:
            if not dimensions:
                self.dimensions = s[1]
            else:
                self.dimensions = dimensions
            data = data.flatten()
        b = self.__class__.buffert
        glBindBuffer(b, self._id)
        glBufferData(b, size, data, _type)
        glBindBuffer(b, 0)


class Ebo(Vbo):  # todo add check for  array type ( it isnt the same as vbo)
    buffert = GL_ELEMENT_ARRAY_BUFFER


class FrameBuffer:
    # todo add more of the colors
    # todo add del, to unbind textures
    # todo add support from renderbuffers
    __default_fb = None
    def __init__(self, color=None, depth=None, stencil=None):
        self._id = glGenFramebuffers(1)
        self._color = color
        self._depth = depth
        self._stencil = stencil

    @classmethod
    def get_default(cls) -> "FrameBuffer":
        if FrameBuffer.__default_fb:
            return FrameBuffer.__default_fb
        else:
            output = FrameBuffer.__new__(FrameBuffer)
            output._id = 0
            output._color = None
            output._depth = None
            output._stencil = None
            FrameBuffer.__default_fb = output
            return output

    def is_complete(self) -> bool:
        glBindFramebuffer(GL_FRAMEBUFFER, self._id)
        output = glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE
        glBindFramebuffer(GL_FRAMEBUFFER, self._id)
        return output

    @property
    def color(self):
        return self._color

    @color.deleter
    def color(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self._id)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, 0, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, self._id)

    @color.setter
    def color(self, tex):
        self._color = tex
        glBindFramebuffer(GL_FRAMEBUFFER, self._id)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex.tex, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, self._id)

    @property
    def depth(self):
        return self._depth

    @depth.setter
    def depth(self, tex):
        self._depth = tex
        glBindFramebuffer(GL_FRAMEBUFFER, self._id)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, tex.tex, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, self._id)

    @property
    def stencil(self):
        return self._stencil

    @stencil.setter
    def stencil(self, tex):
        self._stencil = tex
        glBindFramebuffer(GL_FRAMEBUFFER, self._id)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_STENCIL_ATTACHMENT, GL_TEXTURE_2D, tex.tex, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def _clear(self, mask):
        glClear(mask)

    def clear(self):
        self.clear_all()

    def clear_all(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self._id)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT|GL_STENCIL_BUFFER_BIT)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)