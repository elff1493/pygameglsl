
from OpenGL.GL import *
from OpenGL.GL.shaders import *
import pygame

class Texture:
    active = {}
    default = 0
    __default_tex = None
    def __init__(self):
        # todo add support for all type like rgb rgba...
        self.width = 0
        self.height = 0
        #if surface:
        #    self.width = surface.get_width()
        #    self.height = surface.get_height()
        #    surface = pygame.image.tostring(surface, "RGB", True)
        #   pixel_format = GL_RGB

        self.tex = glGenTextures(1)
        #glBindTexture(GL_TEXTURE_2D, self.tex)
        #glTexImage2D(GL_TEXTURE_2D, 0, pixel_format, self.width, self.height, 0, pixel_format, GL_UNSIGNED_BYTE, surface)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter)
        #glBindTexture(GL_TEXTURE_2D, 0)
        self._format = None
        self._active_index = None
        #self.default += 1
        # self._id = 0
        # self.size = (0, 0)
        #self._surface = surface
    @classmethod
    def get_default(cls):
        if Texture.__default_tex:
            return Texture.__default_tex
        else:
            tex = Texture.__new__(Texture)
            s = pygame.display.get_window_size()
            tex.width = s[0] #glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH)
            tex.height = s[1] #glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT)
            print(tex.width, tex.height)
            tex.tex = 0
            tex._format = None
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
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, GL_NONE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_FUNC, GL_LEQUAL)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, GL_NONE)
        glBindTexture(GL_TEXTURE_2D, 0)
        return t

    @classmethod
    def new_depth(cls):
        t = Texture()
        return t

    @classmethod
    def from_empty(cls):
        t = Texture()
        return t

    def set_filter(self, filter_type):  # todo seter ang geters/ per min/mag
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter_type)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter_type)
        glBindTexture(GL_TEXTURE_2D, 0)

    def set_wrap(self, f):  # todo add all
        """sets how sampling outside the texture will be handled

        """
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, f)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, f)
        glBindTexture(GL_TEXTURE_2D, 0)

    def set_surface(self, surface: pygame.Surface, surface_format=GL_RGB, internal_format=GL_RGB):
        """sets the data of the texture to the data of the surface"""
        textureData = pygame.image.tostring(surface, "RGB", True)  # todo add
        self.width = surface.get_width()
        self.height = surface.get_height()
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, textureData)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)

    def draw_top(self, rect=None):
        """draw the this texture on the screen, on top of the default surface,
        this is done on the gpu and is fast (should be, havent bechmarked)
        """
        if not rect:
            rect = (0, 0, self.width, self.height)
        glViewport(rect[0], rect[1], rect[2], rect[3])
        #glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex2f(-1, 1)
        glTexCoord2f(0, 1)
        glVertex2f(-1, -1)
        glTexCoord2f(1, 1)
        glVertex2f(1, -1)
        glTexCoord2f(1, 0)
        glVertex2f(1, 1)
        glEnd()
        glDisable(GL_TEXTURE_2D)

    def get_surface(self):
        glBindTexture(GL_TEXTURE_2D, self.tex)
        pixels = glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_BYTE)
        surface = pygame.image.fromstring(pixels, (self.width, self.height), "RGBA", True)
        glBindTexture(GL_TEXTURE_2D, 0)
        return surface

    def _bind(self):
        glBindTexture(GL_TEXTURE_2D, self.tex)

    def set_active(self, index):
        glActiveTexture(GL_TEXTURE0 + index)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, 0)
        self._active_index = index