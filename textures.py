
from OpenGL.GL import *
from OpenGL.GL.shaders import *
import pygame
from typing import Union, Iterable, Generic
from consts import Filter, MipMapFilter
from collections.abc import Sequence


class ActiveTextures:
    simpleton = None
    def __new__(cls, *args, **kwargs):
        if not ActiveTextures.simpleton:
            ActiveTextures.simpleton = super(ActiveTextures, cls).__new__(cls, *args, **kwargs)
        return ActiveTextures.simpleton

    def __init__(self):
        self.active = {}

    def __getitem__(self, item):
        return self.active.get(Texture.get_default())

    def __setitem__(self, key: int, value):
        if self.active.get(key):
            self.active[key]._active_index = None
        self.active[key] = value

    def __repr__(self):
        return self.active.__repr__()
    # __class_getitem__?


active_textures = ActiveTextures()


class _TextureBace:
    _t_type = None

    def __init__(self):
        self.tex = glGenTextures(1)
        self._active_index = None
        self.filter = GL_LINEAR

    def _set_active(self, index):

        glActiveTexture(GL_TEXTURE0 + index)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.tex)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, 0)
        self._active_index = index

    def set_active(self, index):
        active_textures[index] = self

    def get_active(self, fallback=None):
        pass

    @property
    def filter(self):
        out = glGetTexParameteriv(self._t_type, GL_TEXTURE_MIN_FILTER)
        return out

    @filter.setter
    def filter(self, filter_type: Filter):
        glBindTexture(self._t_type, self.tex)
        glTexParameteri(self._t_type, GL_TEXTURE_MIN_FILTER, filter_type)
        glTexParameteri(self._t_type, GL_TEXTURE_MAG_FILTER, filter_type)
        glBindTexture(self._t_type, 0)

    @property
    def filter_min(self):
        out = glGetTexParameteriv(self._t_type, GL_TEXTURE_MIN_FILTER)
        return out

    @filter_min.setter
    def filter_min(self, filter_type: Union[Filter, MipMapFilter]):
        glBindTexture(self._t_type, self.tex)
        glTexParameteri(self._t_type, GL_TEXTURE_MIN_FILTER, filter_type)
        glBindTexture(self._t_type, 0)

    @property
    def filter_max(self):
        out = glGetTexParameteriv(self._t_type, GL_TEXTURE_MIN_FILTER)
        return out

    @filter_max.setter
    def filter_max(self, filter_type: Filter):
        glBindTexture(self._t_type, self.tex)
        glTexParameteri(self._t_type, GL_TEXTURE_MIN_FILTER, filter_type)
        glTexParameteri(self._t_type, GL_TEXTURE_MAG_FILTER, filter_type)
        glBindTexture(self._t_type, 0)


class CubeMap(_TextureBace):
    _t_type = GL_TEXTURE_CUBE_MAP
    def __init__(self):
        _TextureBace.__init__(self)
        self.width = 0
        self.height = 0
        #self.tex = glGenTextures(1)
        #self._active_index = None
        #self.set_filter(GL_LINEAR)

    @classmethod
    def from_surfaces(cls, surfaces) -> "CubeMap":
        """pass an itrabale of 6 surfaces"""
        tex = CubeMap()
        tex.set_surfaces(surfaces)
        return tex

    def set_surface(self, surface: pygame.Surface, index: int):
        data = pygame.image.tostring(surface, "RGBA", True)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.tex)
        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + index, 0, GL_RGBA,
                     self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

    def set_surfaces(self, surfaces):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.tex)
        self.width = surfaces[0].get_width()
        self.height = surfaces[0].get_height()
        for i in range(6):
            assert self.width == surfaces[i].get_width()
            assert self.height == surfaces[i].get_height()
            data = pygame.image.tostring(surfaces[i], "RGBA", True)
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGBA,
                         self.width, self.height,
                         0, GL_RGBA, GL_UNSIGNED_BYTE, data)


class Texture(_TextureBace):
    _t_type = GL_TEXTURE_2D
    __default_tex = None
    def __init__(self): # todo add multsampling
        # todo add support for all type like rgb rgba...
        _TextureBace.__init__(self)
        self.width = 0
        self.height = 0


    @classmethod
    def get_default(cls):
        if Texture.__default_tex:
            return Texture.__default_tex
        else:
            tex = Texture.__new__(Texture)
            s = pygame.display.get_window_size()
            tex.width = s[0] #glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH)
            tex.height = s[1] #glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT)
            tex.tex = 0
            tex._active_index = None
            Texture.__default_tex = tex
            return tex


    @classmethod
    def from_surface(cls, surface):
        t = Texture()
        t.set_surface(surface)
        return t

    @classmethod
    def from_size(cls, size, internal_format=GL_RGB, precision=GL_FLOAT):
        t = Texture()
        t.width = size[0]
        t.height = size[1]
        glBindTexture(GL_TEXTURE_2D, t.tex)
        glTexImage2D(GL_TEXTURE_2D, 0, internal_format, t.width, t.height, 0, internal_format, precision, None)
        glBindTexture(GL_TEXTURE_2D, 0)
        return t


    def set_wrap(self, f):  # todo add all
        """sets how sampling outside the texture will be handled

        """
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, f)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, f)
        glBindTexture(GL_TEXTURE_2D, 0)

    def set_surface(self, surface: pygame.Surface, surface_format=GL_RGBA, internal_format=GL_RGBA):
        """sets the data of the texture to the data of the surface"""
        textureData = pygame.image.tostring(surface, "RGBA", True)  # todo add
        self.width = surface.get_width()
        self.height = surface.get_height()
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
        #glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)

    def get_surface(self):
        glBindTexture(GL_TEXTURE_2D, self.tex)
        pixels = glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_BYTE)
        surface = pygame.image.fromstring(pixels, (self.width, self.height), "RGBA", True)
        glBindTexture(GL_TEXTURE_2D, 0)
        return surface


class RenderBuffer:
    def __init__(self): # todo finish renderbuffer
        self._id = glGenRenderbuffers(1)
        self.width = 0
        self.height = 0

    @classmethod
    def from_size(cls, size, internal_format=GL_RGB, multisampling: int = 0):
        rb = RenderBuffer()
        rb.height = size[0]
        rb.width = size[1]
        glBindRenderbuffer(GL_RENDERBUFFER, rb._id)
        if multisampling:
            glRenderbufferStorageMultisample(GL_RENDERBUFFER, multisampling, internal_format, size[0], size[1])
        else:
            glRenderbufferStorage(GL_RENDERBUFFER, internal_format, size[0], size[1])

        return rb
