from OpenGL.GL import *
from OpenGL.GL.shaders import *
import pygame
import numpy
from typing import get_type_hints, TypeVar, Generic
from decomp import Recompiler
import GLSL_helpers as _gl
import sys
FRAG_BACE = """
#version 120

varying vec2 fTexcoords;
uniform sampler2D textureObj;
{uniforms}

void main()
{
{code}
}
{funtions}
"""

def arg_part(f, n):
    def gl_skip_mid(name, value):
        f(name, n, value)
    return gl_skip_mid





class Attribute:...  # todo


class Constant:  # todo
    def __init__(self, _type, value):
        self.value = value
        self.type = _type
        self.name = ""

T = TypeVar("T", _gl.all_types, int)
class Uniform(Generic[T]):
    def __init__(self, _type, value=None, set=True, get=True): # think of better name that dosnt shadow biltin or in
        self.value = value
        self.type = _type
        self.name = ""
        self.set = set
        self.get = get

    def __call__(self, name):
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


def vertex(f):
    if isinstance(f, GlslFuntion) and "vertex" not in f.shader:
        f.shader.append("vertex")
        return f
    return GlslFuntion(f, "vertex")


def fragment(f):
    if isinstance(f, GlslFuntion) and "fragment" not in f.shader:
        f.shader.append("fragment")
        return f
    return GlslFuntion(f, "fragment")


class Texture:
    def __init__(self, surface, filter=GL_LINEAR):
        textureData = pygame.image.tostring(surface, "RGB", True)
        self.width = surface.get_width()
        self.height = surface.get_height()
        self.tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, textureData)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter)
        glBindTexture(GL_TEXTURE_2D, 0)
        #self._id = 0
        #self.size = (0, 0)
        self._surface = surface

    def set_surface(self, surface: pygame.Surface):
        textureData = pygame.image.tostring(surface, "RGB", True)
        self.width = surface.get_width()
        self.height = surface.get_height()
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, textureData)

    def draw_top(self):
        glActiveTexture(GL_TEXTURE0)
        glEnable(GL_TEXTURE_2D)
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

    def set_image(self):
        pass

    def get_image(self):
        pass

class Shader:
    is_compiled = False
    __fragment = ""
    __vertex = ""
    __uniform_types_set = {int:glUniform1i,
                           float:glUniform1f,
                           _gl.sampler2D:glUniform1i,
                           _gl.vec2:arg_part(glUniform2fv, 1),
                           _gl.vec3:arg_part(glUniform3fv, 1)
                           } # todo compleat types
    __uniform_types_get = {} # todo add

    def __init__(self, texture: Texture):
        self._texture = texture
        self.__texture_uniforms = {}
        self._shader = 0
        self.glsl_fragment = ""
        self.glsl_vertex = ""
        self.glsl_funtions = []  # [getattr(self, i) for i in dir(self) if isinstance(getattr(self, i), GlslFuntion)]
        self.__comp = Recompiler([]) # todo move, dont need to keep a refrace all the time
        #self.__comp.debug = True
        self._fb_obj = None
        self.program = None
        self.__uniform_name = {}
        self._viewport = 0, 0, self._texture.width, self._texture.height
        self.tex = 0

    def __arg_part(self, f, n):
        p = self.program

        def gl_skip_mid(name, value):
            f(name, n, value)

        return gl_skip_mid


    def set_uniform(self, name, *value, _type="none"): # todo find a more direct way?
        """set the uniform, this should only be called in shader context"""
        if _type == "none":
            _type = type(value[0])
        Shader.__uniform_types_set[_type](self.__uniform_name[name], *value)

    def get_uniform(self, name, value):
        """wip"""
        pass  # add get

    def viewport(self, x, y, w, h):
        """set the view port. the view port by default is the size of the texture"""
        self._viewport = (x, y, w, h)

    def render(self):
        """render the shader on to the texture"""
        for i, j in enumerate(self.__texture_uniforms):
            glActiveTexture(GL_TEXTURE0+i)
            glBindTexture(GL_TEXTURE_2D, self.__texture_uniforms[j].tex)
        glViewport(*self._viewport)
        glUseProgram(self.program)
        #glActiveTexture(GL_TEXTURE2)
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb_obj)
        #glBindTexture(GL_TEXTURE_2D, self._texture.tex)
        #glActiveTexture(GL_TEXTURE1)
        #glBindTexture(GL_TEXTURE_2D, self.tex)
        glDrawArrays(GL_QUADS, 0, 4)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glUseProgram(0)

    def _uniform_bach(self):
        pass

    def compile(self):
        """compile the shader for use and create atrabute seter and getters"""
        if hasattr(self.__class__, "is_compiled"):
            if self.is_compiled:
                return
        self.__class__.is_compiled = True
        self.__class__.__fragment = ""
        self.__class__.__vertex = ""
        uo = [getattr(self, i)(i) for i in dir(self) if isinstance(getattr(self, i), Uniform)]
        u = [(j.value, j.type, j.name) for j in
             uo]

        self.glsl_funtions = [getattr(self, i) for i in dir(self) if isinstance(getattr(self, i), GlslFuntion)]
        self.__comp.functions = self.glsl_funtions
        self.__comp.uniforms = u
        m = sys.modules[self.__module__]
        for i in dir(m):
            if getattr(m, i) == _gl:
                self.__comp.import_as = i
                break
        #self.__comp.globals = globals()
        self.__comp.run()

        self.glsl_fragment = self.__comp.fragment
        self.glsl_vertex = self.__comp.vertex

        vertexShader = compileShader(self.glsl_vertex, GL_VERTEX_SHADER)
        fragmentShader = compileShader(self.glsl_fragment, GL_FRAGMENT_SHADER)

        self.program = glCreateProgram()
        glAttachShader(self.program, vertexShader)
        glAttachShader(self.program, fragmentShader)
        glLinkProgram(self.program)

        self._fb_obj = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb_obj)
        glBindTexture(GL_TEXTURE_2D, self._texture.tex)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self._texture.tex, 0)

        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            print("incomplete framebuffer object")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glBindTexture(GL_TEXTURE_2D, 0)
        #class_types = self.__annotations__
        #print(class_types)
        self.__uniform_types_set = {int: glUniform1i,
                                    float: glUniform1f,
                                    _gl.sampler2D: glUniform1i,
                                    _gl.vec3: self.__arg_part(glUniform3fv, 1)
                                    }  # todo compleat types

        for v, t, n in u:
            self.__uniform_name[n] = glGetUniformLocation(self.program, n)
            setattr(self.__class__, n, self.f_gen(n, t))

        vertices = [-1, -1,
                    -1, 1,
                    1, 1,
                    1, -1]

        texcoords = [-1, -1,
                     -1, 1,
                     1.0, 1.0,
                     1.0, -1]

        vertices = numpy.array(vertices, dtype=numpy.float32)
        texcoords = numpy.array(texcoords, dtype=numpy.float32)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, vertices)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, texcoords)
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)

    def f_gen(self, name, _type):
        uset = Shader.__uniform_types_set[_type]
#        uget = Shader.__uniform_types_get[_type]
        uname = self.__uniform_name[name]
        p = self.program
        if _type == _gl.sampler2D:
            def set_from_texture(self, value):
                #print(value.tex)
                self.__texture_uniforms[uname] = value
                #glUseProgram(p)
                #uset(uname, value.tex)
                #glUseProgram(0)
            return property(fset=set_from_texture)
        #print("setd:", _type)
        def set_uniform(_, value):

            glUseProgram(p)
            uset(uname, value)
            glUseProgram(0)

        def get_uniform(self, value):
            uget(uname, value)

        return property(fset=set_uniform)


def hw_flip():
    surface = pygame.display.get_surface()
    surface_rect = surface.get_rect()
    glViewport(0, 0, surface_rect.width, surface_rect.height)
    rgb_surface = pygame.image.tostring(surface, 'RGB')
    glUseProgram(0)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, 0)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, surface_rect.width, surface_rect.height, 0, GL_RGB, GL_UNSIGNED_BYTE,
                 rgb_surface)
    glEnable(GL_TEXTURE_2D)

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
    # pygame.display.flip()