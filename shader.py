from OpenGL.GL import *
from OpenGL.GL.shaders import *
import pygame
import numpy
import numpy as np
import ctypes
from typing import TypeVar, Generic, Union
from decomp import Recompiler
import glsl as _gl
from glsl import v1_10 as _v1_10
from glsl import v1_20 as _v1_20
from glsl import v1_30 as _v1_30
from glsl import v1_40 as _v1_40
from glsl import v1_50 as _v1_50
from glsl import v3_30 as _v3_30
from glsl import v4_10 as _v4_10
from glsl import v4_20 as _v4_20
from glsl import v4_30 as _v4_30
from glsl import v4_40 as _v4_40
from glsl import v4_50 as _v4_50
from glsl import v4_60 as _v4_60
import glsl as _glsl
import sys

from gl_types import *
from buffers import *

NEAREST = GL_NEAREST
LINEAR = GL_LINEAR
GL_DEPTH_COMPONENT = GL_DEPTH_COMPONENT
clear = glClear
colorb = GL_COLOR_BUFFER_BIT


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
    active = {}
    default = 0

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
        self.default += 1
        # self._id = 0
        # self.size = (0, 0)
        #self._surface = surface

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

    def draw_top(self, rect=None):  # todo inplemnt
        """draw the this texture on the screen, on top of the default surface,
        this is done on the gpu and is fast (should be havent bechmarked)
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



_uniform_types_set = {
        Texture: glUniform1i,
        _gl.sampler2D: glUniform1i,
        float: glUniform1f,
        _gl.vec2: glUniform2f,
        _gl.vec3: lambda n, v :glUniform3f(n, v[0], v[1], v[2]),
        _gl.vec4: glUniform4f,
        int: glUniform1i,
        _gl.ivec2: glUniform2i,
        _gl.ivec3: glUniform3i,
        _gl.ivec4: glUniform4i,
        _gl.mat4: lambda pos, v: glUniformMatrix4fv(pos, True, 1, v)
        # glUniform1ui # glUniform2ui # glUniform3ui # glUniform4ui
        #
        # glUniform1fv # glUniform2fv # glUniform3fv # glUniform4fv
        #
        # glUniform1iv # glUniform2iv # glUniform3iv # glUniform4iv
        #
        # glUniform1uiv # glUniform2uiv # glUniform3uiv # glUniform4uiv
        #
        # glUniformMatrix2fv # glUniformMatrix3fv # glUniformMatrix4fv # glUniformMatrix2x3fv
        # glUniformMatrix3x2fv # glUniformMatrix2x4fv # glUniformMatrix4x2fv # glUniformMatrix3x4fv
        # glUniformMatrix4x3fv

    }


class ShaderCompute:
    def __init__(self):
        pass
    @classmethod
    def function(cls, f):
        """decorator for glsl function"""
        return GlslFuntion(f, "vertex")

    def run(self):
        pass

class ShaderTessEvaluation:
    def __init__(self):
        self.program: Program = None

class ShaderTessControl:
    def __init__(self):
        self.program: Program = None


class ShaderGeometry:
    def __init__(self, max_vertices, in_type, out_type):
        self.program: Program = None
        self._translation = (max_vertices, in_type, out_type)


class ShaderVertex:
    def __init__(self, vao):
        self.vao = vao
        self.program: Program = None

    @classmethod
    def function(cls, f):
        """decorator for glsl function"""
        return GlslFuntion(f, "vertex")

    def set_vao(self, vao: Vao):
        self.vao = vao

    def _get_data(self):
        glvar = [getattr(self, i) for i in dir(self) if isinstance(getattr(self, i), GlslVariable)]
        funtions = [getattr(self, i).callback for i in dir(self) if isinstance(getattr(self, i), GlslFuntion)]
        return glvar, funtions


class ShaderFragment:
    #in
    gl_FragCoord: int
    gl_FrontFacing: bool
    gl_ClipDistance: float  # todo array
    gl_CullDistance: float  # todo array
    gl_PointCoord: _gl.vec2
    gl_PrimitveID: int
    gl_SampleID: int
    gl_SamplePositon: _gl.vec2
    gl_SampleMaskIn: _gl.vec2  # todo arry
    gl_Layer: int
    gl_ViewportIndex: int
    gl_HelperInvocaton: bool
    # out
    gl_FragDepth: float
    gl_SampleMask: int

    def __init__(self, texture: Texture):
        self._texture = texture
        self.program: Program = None

    @classmethod
    def function(cls, f):
        """decorator for glsl function"""
        return GlslFuntion(f, "fragment")

    def _get_data(self):
        glvar = [getattr(self, i) for i in dir(self) if isinstance(getattr(self, i), GlslVariable)]
        funtions = [getattr(self, i).callback for i in dir(self) if isinstance(getattr(self, i), GlslFuntion)]
        return glvar, funtions


class ShaderDefault:  # placeolder
    """if this is set as a shader the defult shader for that part of the pipline will be used"""
    pass


class Program:
    """class to wrap the opengl shader pipline"""
      # todo compleat types

    def __init__(self):
        self._id = 0
        self._fb = 0
        self._vao = None

        self._target_c = None  # todo setters / getters
        self._target_d = None
        self._target_s = None

        self.fragment: Union[ShaderFragment, None] = None
        self.geometry: Union[ShaderGeometry, None] = None
        self.vertex: Union[ShaderVertex, None] = None
        self.tess_evaluation: Union[ShaderTessEvaluation, None ] = None
        self.tess_control: Union[ShaderTessControl, None] = None
        # cant use compute shader in this pipline, it has its own pipline
        self.options = Options()
        self.debug = False
        self.version = 120  # todo make default to latest
        self._viewport = 0, 0, 100, 100  # todo make not default to 100
        self.__active_textures = {}  # key is name, value is texture

    def clear(self):
        glUseProgram(self._id)
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb)
        glClearColor(0.1, 0.1, 0.1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def cleard(self):
        glUseProgram(self._id)
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb)
        glClearColor(0.1, 0.1, 0.1, 1)
        glClear(GL_DEPTH_BUFFER_BIT)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def render_vao(self, start=None, count=None, primitive=GL_TRIANGLES):
        """render the vao"""
        #glEnableClientState(GL_VERTEX_ARRAY)

        glViewport(*self._viewport)
        glUseProgram(self._id)
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb)
        if start is None:  # default
            start = 0
        if count is None:  # assume size
            count = self._vao[0].len - start
        glBindVertexArray(self._vao._id)
        glDrawArrays(primitive, start, count)  # todo indexing
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glUseProgram(0)

    def render_instance(self, n,  start=None, count=None, primitive=GL_TRIANGLES): # todo
        glViewport(*self._viewport)
        glUseProgram(self._id)
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb)
        if start is None:  # default
            start = 0
        if count is None:  # assume size
            count = self._vao[0].len - start
        glBindVertexArray(self._vao._id)
        glDrawArraysInstanced(primitive, start, count, n)  # todo indexing
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glUseProgram(0)

    def render_vao_indexed(self, ebo: Ebo, start=None, count=None, primitive=GL_TRIANGLES):
        # todo add start
        glViewport(*self._viewport)
        glUseProgram(self._id)
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb)
        if start is None:  # default
            start = 0
        if count is None:  # assume size
            count = self._vao[0].len - start
        glBindVertexArray(self._vao._id)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo._id)
        glDrawElements(primitive, ebo.len, ebo.type, None)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glUseProgram(0)

    def render(self):
        """render the shader on to the texture"""
        glViewport(*self._viewport)
        glUseProgram(self._id)
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb)

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

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glUseProgram(0)

    def _compile_shader(self):
        pass

    def compile(self):  # todo make it not so long
        # 1. analise the objects
        self._target_c = self.fragment._texture
        self._vao = self.vertex.vao
        shader_obs = [self.fragment,
                   self.vertex,
                   self.geometry,
                   self.tess_control,
                   self.tess_evaluation]
        shader_obs = [i for i in shader_obs if i is not None]

        # get uniforms, Attributes, piping varables, can be defined in any shader
        uniforms = {}
        attribute = []
        glsl_varables = []
        to_remove = []
        for ob in shader_obs:
            # set program
            ob.program = self
            # get all
            attribute.extend([getattr(ob, i).set(i) for i in dir(ob) if isinstance(getattr(ob, i), Attribute)])
            glsl_varables.extend([getattr(ob, i).set(i) for i in dir(ob) if isinstance(getattr(ob, i), GlslVariable)])
            for i in dir(ob):
                if isinstance(getattr(ob, i), Uniform):
                    uniforms[i] = getattr(ob, i).set(i)
            # find what modual was used for this shader
            # this is needed so glsl works right with "as" imports
            m = sys.modules[ob.__module__]
            for i in dir(m):
                if getattr(m, i) in (_gl, _glsl, _v1_10, _v1_20,
                                     _v1_30, _v1_40, _v1_50, _v3_30,
                                     _v4_10, _v4_20, _v4_30, _v4_40,
                                     _v4_50, _v4_60):
                    to_remove.append(i)
                    break
        uniforms = list(uniforms.values())

        # 2. ast compile, opengl compile
        compiler = Recompiler([])
        compiler.version = self.version
        compiler.debug = self.debug
        compiler.import_as = to_remove
        # get what the modual is imported as, to remove so glsl works right
        # todo add removes here
        # compiler.attributes = a # todo add inouts

        # add all shaders to decompilers
        u = [(j.value, j.type, j.name) for j in
             uniforms]
        a = [(j.type, j.name) for j in attribute]  # todo remove dependancy
        if self.fragment is not None:  # todo tidy up
            temp = self.fragment._get_data()  # gets (glslvar, funtions)
            compiler.fragment = ((None,), u, temp[0], temp[1], None)
        if self.vertex is not None:
            temp = self.vertex._get_data()
            compiler.vertex = ((None,), u, temp[0], temp[1], a)

        if self.geometry is not None: #todo implemen
            raise Exception("not supported yet")

        if self.tess_control is not None:
            raise Exception("not supported yet")

        if self.tess_evaluation is not None:
            raise Exception("not supported yet")

        # todo geomrtry
        # todo tess controll
        # todo tess eval
        # todo add all

        codes = compiler.run()
        key_code = {ShaderFragment: "fragment",
                    ShaderVertex: "vertex",
                    ShaderGeometry: "geometry",
                    ShaderTessControl: "tess_control",
                    ShaderTessEvaluation: "tess_evaluation"
                    }

        # 2.5 opengl part
        shaders = []  # for clean up
        keys = {ShaderFragment: GL_FRAGMENT_SHADER,
                ShaderVertex: GL_VERTEX_SHADER,
                ShaderGeometry: GL_GEOMETRY_SHADER,
                ShaderTessEvaluation: GL_TESS_EVALUATION_SHADER,
                ShaderTessControl: GL_TESS_CONTROL_SHADER
                }

        for i in shader_obs:
            t = [bace for bace in i.__class__.__bases__ if bace in keys.keys()]
            if len(t) == 0:
                raise Exception("not a valid shader")
            elif len(t) > 1:
                raise Exception("more than one shader base is not compatible")
            t = t[0]
            i.glsl = codes[key_code[t]]
            shaders.append(compileShader(i.glsl, keys[t]))

        self._id = glCreateProgram()
        for i in shaders:
            glAttachShader(self._id, i)

        for a in attribute:  # set attribute location, needs to be done before linking
            glBindAttribLocation(self._id, a.index, a.name)

        glLinkProgram(self._id)
        # clean up
        for i in shaders:
            glDeleteShader(i)
        if not glGetProgramiv(self._id, GL_LINK_STATUS):
            raise Exception("shader link error")

        # 3. seters, geters
        for ob in shader_obs:
            for u in uniforms:  # todo find a object baced way for nice setters and geters
                setattr(ob.__class__, u.name, self.__getter(u.name, u.type))

        # 4. init, shader is compiled, just need to set up thing that cant be set up beforhand

        self._fb = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb)
        #glBindTexture(GL_TEXTURE_2D, self._.tex)

        # todo mutiple colour buffers

        if self._target_s:
            self._viewport = 0, 0, self._target_s.width, self._target_s.height
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_STENCIL_ATTACHMENT, GL_TEXTURE_2D, self._target_c.tex, 0)

        if self._target_d:
            self._viewport = 0, 0, self._target_d.width, self._target_d.height
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self._target_d.tex, 0)

        if self._target_c:
            self._viewport = 0, 0, self._target_c.width, self._target_c.height
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self._target_c.tex, 0)

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            t = glCheckFramebufferStatus(GL_FRAMEBUFFER)
            raise Exception("frame buffer error - incomplete " + str(t))

        glBindFramebuffer(GL_FRAMEBUFFER, 0)


    def __getter(self, name, _type):
        uset = _uniform_types_set[_type]
        uname = glGetUniformLocation(self._id, name)
        p = self._id
        if _type in (_gl.sampler2D, Texture):
            def set_from_texture(self, value):
                glUseProgram(p)
                if type(value) is Texture:
                    if value._active_index is None:
                        raise ValueError("Texture is not active, can not set uniform")
                    print("set as", value._active_index)
                    uset(uname, value._active_index)
                elif type(value) is int:
                    uset(uname, value)
                glUseProgram(0)

            return property(fset=set_from_texture)

        def set_uniform(_, value):
            glUseProgram(p)
            uset(uname, value)
            glUseProgram(0)

        def get_uniform(_): # todo add some getters, most are errors i think tho
            return Exception("this getter is not suppoted")

        return property(fset=set_uniform, fget=get_uniform)
# todo test multipul shaders


class Options:
    def __init__(self):
        pass
    @property
    def DEPTH_TEST(self):
        return glGetBooleanv(GL_DEPTH_TEST)

    @DEPTH_TEST.setter
    def DEPTH_TEST(self, value):
        if value:
            glEnable(GL_DEPTH_TEST)
        else:
            glDisable(GL_DEPTH_TEST)

    @property
    def DepthMask(self):
        return None

    @DepthMask.setter
    def DepthMask(self, value):
        glDepthMask(value)

    @property
    def ClearDepth(self):
        return None

    @ClearDepth.setter
    def ClearDepth(self, value):
        glClearDepth(value)

    @property
    def ClearDepth(self):
        return None

    @ClearDepth.setter
    def ClearDepth(self, value):
        glClearDepth(value)

    @property
    def DepthFunc(self):
        return None

    @DepthFunc.setter
    def DepthFunc(self, value):
        glDepthFunc(value)

    @property
    def ALPHA_TEST(self):
        return None

    @ALPHA_TEST.setter
    def ALPHA_TEST(self, value):
        if value:
            glEnable(GL_ALPHA_TEST)
        else:
            glDisable(GL_ALPHA_TEST)

    @property
    def ALPHA_TEST(self):
        return None

    @ALPHA_TEST.setter
    def ALPHA_TEST(self, value):
        if value:
            glEnable(GL_ALPHA_TEST)
        else:
            glDisable(GL_ALPHA_TEST)


class Shader:
    # in
    gl_FragCoord: _gl.vec4
    gl_FrontFacing: bool
    gl_PointCoord: _gl.vec2
    # out
    gl_FragColor: _gl.vec4  # removed after v3.1,
    # define your own output with
    # self.foo = GlslVariable(piping=OUT)

    def __init__(self, texture: Texture):
        self._texture = texture
        self.__texture_uniforms = {}
        self.glsl_fragment = ""
        self._fb_obj = None
        self.program = None
        self.__uniform_name = {}
        self._viewport = 0, 0, self._texture.width, self._texture.height
        self.debug = False

    def set_target(self, texture):
        """set target to render to, requires compilation"""
        self._texture = texture
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb_obj)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self._texture.tex, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def viewport(self, x, y, w, h):
        """set the view port. the view port by default is the size of the texture (set when compiled)"""
        self._viewport = (x, y, w, h)

    def render(self):
        """render the shader on to the texture target"""
        #print(self.__texture_uniforms)
        #for i, j in enumerate(self.__texture_uniforms):
            #print(i, j, "tex")
            #glActiveTexture(GL_TEXTURE0 + i)
            #glBindTexture(GL_TEXTURE_2D, self.__texture_uniforms[j].tex)
        glViewport(*self._viewport)
        glUseProgram(self.program)
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb_obj)
        glDrawArrays(GL_QUADS, 0, 4)


        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glUseProgram(0)

    def compile_from_string(self, code):
        v = """
#version 120
attribute vec2 vPosition;
attribute vec2 vTexcoords;
varying vec2 {0};
void main()
{{
    gl_Position = vec4(vPosition.x, vPosition.y, 0.0, 1.0);
    {0} = vTexcoords;
}}
        """
        uo = [getattr(self, i).set(i) for i in dir(self) if isinstance(getattr(self, i), Uniform)]
        glname = [getattr(self, i).set(i) for i in dir(self) if isinstance(getattr(self, i), GlslVariable)]
        glin = [i for i in glname if i.inout == IN]
        if len(glin) > 1:
            raise Exception("multiple in values not aloud")
        if not glin:
            glin = "fragCoord"
        else:
            glin = glin[0].name
        if self.debug:
            print(v.format(glin))
        default_vertex = compileShader(v.format(glin), GL_VERTEX_SHADER)
        fragmentShader = compileShader(code, GL_FRAGMENT_SHADER)

        self.program = glCreateProgram()
        glAttachShader(self.program, fragmentShader)
        glAttachShader(self.program, default_vertex)
        glLinkProgram(self.program)
        glDeleteShader(fragmentShader)
        glDeleteShader(default_vertex)

        self._fb_obj = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb_obj)
        glBindTexture(GL_TEXTURE_2D, self._texture.tex)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self._texture.tex, 0)

        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            raise Exception("frame buffer error - incomplete")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        for i in uo:
            self.__uniform_name[i.name] = glGetUniformLocation(self.program, i.name)
            setattr(self.__class__, i.name, self.f_gen(i.name, i.type))

        vertices = [-1, -1,
                    -1, 1,
                    1, 1,
                    1, -1]

        texcoords = [0, 0,
                     0, 1,
                     1.0, 1.0,
                     1.0, 0]

        vertices = numpy.array(vertices, dtype=numpy.float32)
        texcoords = numpy.array(texcoords, dtype=numpy.float32)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, vertices)  # todo find better way
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, texcoords)
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)

    def __get_code(self, u):
        funtions = [getattr(self, i).callback for i in dir(self) if isinstance(getattr(self, i), GlslFuntion)]
        compiler = Recompiler([])
        compiler.debug = self.debug
        u = [(j.value, j.type, j.name) for j in u]
        glvar = [getattr(self, i).set(i) for i in dir(self) if isinstance(getattr(self, i), GlslVariable)]
        compiler.fragment = ((None,), u, glvar, funtions, None)

        m = sys.modules[self.__module__]
        for i in dir(m):
            if getattr(m, i) in (_gl, _glsl, _v1_10, _v1_20,
                                 _v1_30, _v1_40, _v1_50, _v3_30,
                                 _v4_10, _v4_20, _v4_30, _v4_40,
                                 _v4_50, _v4_60):
                compiler.import_as = i
                break

        return compiler.run()["fragment"]

    def compile(self):
        """compile the shader for use and create attribute setter and getters"""
        uo = [getattr(self, i).set(i) for i in dir(self) if isinstance(getattr(self, i), Uniform)]

        code = self.__get_code(uo)
        self.compile_from_string(code)

    def f_gen(self, name, _type):

        uset = _uniform_types_set[_type]
        uname = self.__uniform_name[name]
        p = self.program
        if _type == _gl.sampler2D:
            def set_from_texture(self, value):

                self.__texture_uniforms[uname] = value
                glUseProgram(p)
                if type(value) is Texture:
                    if value._active_index is None:
                        raise ValueError("Texture is not active, can not set uniform")
                    uset(uname, value._active_index)
                elif type(value) is int:
                    uset(uname, value)
                glUseProgram(0)

            return property(fset=set_from_texture)
        elif _type in (int, float, bool):  # todo make robust
            def set_uniform(_, value):
                glUseProgram(p)
                uset(uname, value)
                glUseProgram(0)
        else:
            def set_uniform(_, value):  # more then one value

                glUseProgram(p)
                uset(uname, *value)
                glUseProgram(0)
        return property(fset=set_uniform)


def hw_flip():
    surface = pygame.display.get_surface()
    surface_rect = surface.get_rect()
    glViewport(0, 0, surface_rect.width, surface_rect.height)
    rgb_surface = pygame.image.tostring(surface, 'RGB')
    glUseProgram(0)
    #glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, 0)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, surface_rect.width, surface_rect.height, 0, GL_RGB, GL_UNSIGNED_BYTE,
                 rgb_surface)
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
