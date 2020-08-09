from OpenGL.GL import *
from OpenGL.GL.shaders import *
import pygame
import numpy
import numpy as np
import ctypes
from typing import TypeVar, Generic
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


NEAREST = GL_NEAREST
LINEAR = GL_LINEAR


class GlslArrayProxy:
    def __init__(self, name):
        self.name = name
        self.id = 0

    def set(self, x):
        pass

    def get(self):
        pass


class Attribute:
    def __init__(self, _type, index):  # think of better name that dosnt shadow biltin or in
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


class GlslVariable:
    def __init__(self, _type, piping=AUTO):  # todo rename
        self.type = _type
        self.inout = piping
        self.name = ""

    def set(self, name):
        self.name = name
        return self


class Constant:  # todo
    def __init__(self, _type, value):
        self.value = value
        self.type = _type
        self.name = ""


T = TypeVar("T", _gl.all_types, int)


class Uniform(Generic[T]):
    def __init__(self, _type, value=None):  # think of better name that dosnt shadow biltin or in
        self.value = value
        self.type = _type
        self.name = ""

    def set(self, name):  # todo remove, bad practis
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
    def __init__(self, surface, filter=LINEAR):
        # todo add support for all type like rgb rgba...
        textureData = pygame.image.tostring(surface, "RGB", True)
        self.width = surface.get_width()
        self.height = surface.get_height()
        self.tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, textureData)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter)
        glBindTexture(GL_TEXTURE_2D, 0)
        # self._id = 0
        # self.size = (0, 0)
        self._surface = surface

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

    def set_surface(self, surface: pygame.Surface):
        """sets the data of the texture to the data of the surface"""
        textureData = pygame.image.tostring(surface, "RGB", True)
        self.width = surface.get_width()
        self.height = surface.get_height()
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, textureData)

    def draw_top(self, rect=None):  # todo inplemnt
        """draw the this texture on the screen, on top of the default surface,
        this is done on the gpu and is fast
        """
        if not rect:
            rect = (0, 0, self.width, self.height)
        glViewport(rect[0], rect[1], rect[2], rect[3])
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
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
    _types = {np.byte: GL_BYTE,
              np.ubyte: GL_UNSIGNED_BYTE,
              np.short: GL_SHORT,
              np.ushort: GL_UNSIGNED_SHORT,
              np.intc: GL_INT,
              np.uintc: GL_UNSIGNED_INT}

    def __init__(self):
        self._id = glGenBuffers(1)
        self.dimensions = None
        self.len = 0
        self.type = GL_INT
        self.normalised = False

    def set_data(self, data: numpy.array, _type=GL_DYNAMIC_DRAW):  # todo split up
        #data = numpy.array([1, 2, 3], int)
        size = data.nbytes
        s = data.shape
        #print(s)

        self.len = s[0]
        #print(type(data.dtype), data.dtype, dir(numpy.intc))
        self.type = Vbo._types[data.dtype.type]

        if len(s) > 2:
            raise Exception("invalid array shape")
        if len(s) > 1:
            self.dimensions = s[1]
            data = data.flatten()

        glBindBuffer(GL_ARRAY_BUFFER, self._id)
        glBufferData(GL_ARRAY_BUFFER, size, data, _type)
        glBindBuffer(GL_ARRAY_BUFFER, 0)



_uniform_types_set = {
        Texture: glUniform1i,
        _gl.sampler2D: glUniform1i,
        float: glUniform1f,
        _gl.vec2: glUniform2f,
        _gl.vec3: glUniform3f,
        _gl.vec4: glUniform4f,
        int: glUniform1i,
        _gl.ivec2: glUniform2i,
        _gl.ivec3: glUniform3i,
        _gl.ivec4: glUniform4i,
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
    pass


class ShaderTessEvaluation:
    pass


class ShaderTessControl:
    pass


class ShaderGeometry:
    pass


class ShaderVertex:
    def __init__(self, vao):
        self.vao = vao

    def set_vao(self, vao: Vao):
        self.vao = vao

    def _get_data(self):
        glvar = [getattr(self, i) for i in dir(self) if isinstance(getattr(self, i), GlslVariable)]
        funtions = [getattr(self, i).callback for i in dir(self) if isinstance(getattr(self, i), GlslFuntion)]
        return glvar, funtions


class ShaderFragment:  # todo split shader types up, avoid god object/ support blank shaders
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
        self.program = None

    def compile(self):
        p = Program()
        p.fragment = self
        p._target_c = self._texture # todo seter and getrer
        p.compile()

    def render(self):
        self.program.render()

    def _get_data(self):
        glvar = [getattr(self, i) for i in dir(self) if isinstance(getattr(self, i), GlslVariable)]
        funtions = [getattr(self, i).callback for i in dir(self) if isinstance(getattr(self, i), GlslFuntion)]
        return glvar, funtions


class ShaderDefault: # placeolder
    """if this is set as a shader the defult shader for that part of the pipline will be used"""
    pass


class Program:
    """class to wrap the opengl shader pipline"""
      # todo compleat types

    def __init__(self):
        self._id = 0
        self._fb = 0
        self._vao = None


        self._target_c = None
        self._target_d = None
        self._target_s = None

        self.fragment = ShaderDefault()
        self.geometry = ShaderDefault()
        self.vertex = ShaderDefault()
        self.tess_evaluation = ShaderDefault()
        self.tess_control = ShaderDefault()
        # cant use compute shader in this pipline, it has its own
        self.debug = False
        self._viewport = 0, 0, 100, 100
        self.__active_textures = {} # key is name, value is texture

    def render_vao(self, start=None, count=None):
        """render the vao"""
        #glEnableClientState(GL_VERTEX_ARRAY)
        for i, j in enumerate(self.__active_textures):
            if j != -1:
                glActiveTexture(GL_TEXTURE0 + i)
                glBindTexture(GL_TEXTURE_2D, self.__active_textures[j].tex)
        glViewport(*self._viewport)
        glUseProgram(self._id)
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb)
        if start is None:
            start = 0
        if count is None:
            count = self._vao[0].len - start
        glBindVertexArray(self._vao._id)
        glDrawArrays(GL_TRIANGLES, start, count)  # todo indexing
        # todo set render type
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glUseProgram(0)

    def render_instance(self, n):
        pass

    def render(self):
        """render the shader on to the texture"""
        for i, j in enumerate(self.__active_textures):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, self.__active_textures[j].tex)
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

    def compile(self): # todo make it not so long
        # 1. analise the objects
        self._target_c = self.fragment._texture
        self._vao = self.vertex.vao
        shader_obs = [self.fragment,
                   self.vertex,
                   self.geometry,
                   self.tess_control,
                   self.tess_evaluation]
        shader_obs = [i for i in shader_obs if i.__class__ is not ShaderDefault]

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
            #uniforms.extend([getattr(ob, i).set(i) for i in dir(ob) if isinstance(getattr(ob, i), Uniform)])
            # find what modual was used for this shader
            # this is needed so glsl works right
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
        compiler = Recompiler([])  # todo make new for all pipiline
        compiler.debug = True  # self.debug
        #compiler.functions = [getattr(self, i) for i in dir(self) if isinstance(getattr(self, i), GlslFuntion)]
        #compiler.uniforms = [(j.value, j.type, j.name) for j in uniforms]
        compiler.import_as = to_remove
        # get what the modual is imported as, to remove so glsl works right
        # todo add removes here
        # compiler.attributes = a # todo add inouts

        # add all shaders to decompilers
        u = [(j.value, j.type, j.name) for j in
             uniforms]
        print("aa", attribute)
        a = [(j.type, j.name) for j in attribute]  # todo remove dependancy
        if self.fragment.__class__ is not ShaderDefault:  # todo tidy up
            temp = self.fragment._get_data()  # gets (glslvar, funtions)
            compiler.fragment = ((None,), u, temp[0], temp[1], None)
        if self.vertex.__class__ is not ShaderDefault:
            temp = self.vertex._get_data()
            print(a)
            compiler.vertex = ((None,), u, temp[0], temp[1], a)
        # todo add all

        codes = compiler.run()
        key_code = {ShaderFragment: "fragment",
                    ShaderVertex: "vertex"}

        # 2.5 opengl part
        shaders = []
        keys = {ShaderFragment: GL_FRAGMENT_SHADER,
                ShaderVertex: GL_VERTEX_SHADER
                } # todo more shadres
        for i in shader_obs:
            t = [bace for bace in i.__class__.__bases__ if bace in keys.keys()]
            if len(t) == 0:
                print(i)
                raise Exception("not a valid shader")
            elif len(t) > 1:
                raise Exception("more than one shader bace is not compatable")
            t = t[0]
            print(t)
            i.glsl = codes[key_code[t]]
            s = compileShader(i.glsl, keys[t])
            shaders.append(s)
            #if glGetShaderiv(s) todo add shader compile error
        self._id = glCreateProgram()
        for i in shaders:
            glAttachShader(self._id, i)

        for a in attribute:
            glBindAttribLocation(self._id, a.index, a.name)
            #a.set_index()

        glLinkProgram(self._id)

        for i in shaders:
            glDeleteShader(i)

        if not glGetProgramiv(self._id, GL_LINK_STATUS):  # todo test
            raise Exception("shader link error")

        # 3. seters, geters
        for ob in shader_obs:
            for u in uniforms: # todo
            #self.__uniform_name[i.name] = glGetUniformLocation(self._id, i.name)
                setattr(ob.__class__, u.name, self.__getter(u.name, u.type))

        #4. init, shader is compiled, just need to set up thing that cant be set up beforhand

        self._fb = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb)
        #glBindTexture(GL_TEXTURE_2D, self._.tex)
        if self._target_c:
            glBindTexture(GL_TEXTURE_2D, self._target_c.tex)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self._target_c.tex, 0)
        # todo mutiple colour buffers
        if self._target_d:
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self._target_d.tex, 0)
        if self._target_s:
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_STENCIL_ATTACHMENT, GL_TEXTURE_2D, self._target_c.tex, 0)


        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            raise Exception("frame buffer error - incomplete")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        self._viewport = 0, 0, self._target_c.width, self._target_c.height


    def __getter(self, name, _type):
        uset = _uniform_types_set[_type]
        uname = glGetUniformLocation(self._id, name)
        p = self._id
        if _type in (_gl.sampler2D, Texture):
            def set_from_texture(_, value):
                self.__active_textures[uname] = value
            return property(fset=set_from_texture)

        def set_uniform(_, value):
            glUseProgram(p)
            uset(uname, value)
            glUseProgram(0)

        def get_uniform(_): # todo add some getters, most are errors i think tho
            return Exception("this getter is not suppoted")

        return property(fset=set_uniform, fget=get_uniform)
# todo test multipul shaders


class Shader:

    __uniform_types_get = {}  # todo add

    def __init__(self, texture: Texture):
        self._texture = texture
        self.__texture_uniforms = {}
        self.glsl_fragment = ""
        #self.glsl_funtions = []  # [getattr(self, i) for i in dir(self) if isinstance(getattr(self, i), GlslFuntion)]
        # self.__comp = Recompiler([]) # todo move, dont need to keep a refrace all the time

        self._fb_obj = None
        self.program = None
        self.__uniform_name = {}
        self._viewport = 0, 0, self._texture.width, self._texture.height
        # self.tex = 0


    def set_target(self, texture):
        """set taget, requires compilation"""
        self._texture = texture
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb_obj)
        # glBindTexture(GL_TEXTURE_2D, self._texture.tex)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self._texture.tex, 0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)


    def viewport(self, x, y, w, h):
        """set the view port. the view port by default is the size of the texture"""
        self._viewport = (x, y, w, h)

    def render(self):
        """render the shader on to the texture"""
        for i, j in enumerate(self.__texture_uniforms):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, self.__texture_uniforms[j].tex)
        glViewport(*self._viewport)
        glUseProgram(self.program)
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb_obj)

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

    def _uniform_bach(self):
        pass

    def compile_from_file(self, fragment_path, vertex_path):  # todo add all shaders
        pass

    def compile(self):
        """compile the shader for use and create atrabute seter and getters"""
        uo = [getattr(self, i).set(i) for i in dir(self) if isinstance(getattr(self, i), Uniform)]
        #glvar = [getattr(self, i).set(i) for i in dir(self) if isinstance(getattr(self, i), GlslVariable)]

        u = [(j.value, j.type, j.name) for j in
             uo]
        #temp = [(j.value, j.type, j.name) for j in
             #uo]
        temp = []
        funtions = [getattr(self, i).callback for i in dir(self) if isinstance(getattr(self, i), GlslFuntion)]
        compiler = Recompiler([])
        # compiler.debug = True
        compiler.fragment = ((None,), u, temp, funtions, None)

        m = sys.modules[self.__module__]
        for i in dir(m):
            if getattr(m, i) in (_gl, _glsl, _v1_10, _v1_20,
                                 _v1_30, _v1_40, _v1_50, _v3_30,
                                 _v4_10, _v4_20, _v4_30, _v4_40,
                                 _v4_50, _v4_60):
                compiler.import_as = i
                break

        code = compiler.run()["fragment"]
        fragmentShader = compileShader(code, GL_FRAGMENT_SHADER)

        self.program = glCreateProgram()
        glAttachShader(self.program, fragmentShader)
        glLinkProgram(self.program)
        glDeleteShader(fragmentShader)

        self._fb_obj = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self._fb_obj)
        glBindTexture(GL_TEXTURE_2D, self._texture.tex)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self._texture.tex, 0)

        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            raise Exception("frame buffer error - incomplete")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        for v, t, n in u:
            self.__uniform_name[n] = glGetUniformLocation(self.program, n)
            setattr(self.__class__, n, self.f_gen(n, t)) # todo make object baceded?

    def f_gen(self, name, _type):

        uset = _uniform_types_set[_type]
        #        uget = Shader.__uniform_types_get[_type]
        uname = self.__uniform_name[name]
        p = self.program
        if _type == _gl.sampler2D:
            def set_from_texture(self, value):
                # print(value.tex)
                self.__texture_uniforms[uname] = value
                glUseProgram(p)
                uset(uname, value.tex)
                glUseProgram(0)

            return property(fset=set_from_texture)

        # print("setd:", _type)
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
