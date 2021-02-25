import pygame
from pygame.locals import *

from shader import Uniform,  ShaderFragment, ShaderVertex, Program, Attribute, GlslVariable, GL_DEPTH_COMPONENT, GL_COLOR_BUFFER_BIT
from buffers import FrameBuffer, Vbo, Vao, Ebo
from textures import Texture, RenderBuffer
import shader as ss
from glsl.v1_10 import sampler2D
from glsl import v1_10 as g
import numpy as np
import math
import glm


def make_matrix(near, far):
    fov = math.radians(90.0)
    out = glm.perspective(fov, 1, 0.01, 100)
    #out = glm.inverse(out)
    return out.to_list()


class MyVertex(ShaderVertex):
    def __init__(self):
        ShaderVertex.__init__(self)

        self.vetex = Attribute[g.vec3](0)
        self.frag = Attribute[g.vec2](1)
        self.normal = Attribute[g.vec3](2)
        self.instance_position = Attribute[g.vec3](3)
        #self.iTime = Uniform(float)
        self.projectionmatrix = Uniform[g.mat4]()
        self.trans = Uniform[g.mat4]()
        self.fragcoord = GlslVariable[g.vec2](piping="out")
        self.pixlenormal = GlslVariable[g.vec3](piping="out")
        self.tolight = GlslVariable[g.vec3](piping="out")
        self.lightp = Uniform[g.vec3]()
        #self.fragnormal = GlslVariable(g.vec3, piping="out")
        self.vertex_buffer = Vbo()
        self.frag_buffer = Vbo()
        self.normals = Vbo()
        self.positions = Vbo()
        self.ebo = Ebo()

        b, n = load_obj("bunny.obj")
        bunny = np.array(b,  np.float32)

        self.ebo.set_data(np.array([i for i in range(len(b))],  np.uintc), dimensions=2)
        self.vertex_buffer.set_data(bunny, dimensions=3)
        self.frag_buffer.set_data(np.array([1 for i in range(2*len(b))],  np.uintc), dimensions=2)
        pos = []
        for x in range(10):
            for y in range(10):
                for z in range(10):
                    pos.append((x*-3, y*-3, z*-3))
        self.positions.set_data(np.array(pos, np.intc))

        self.normals.set_data(np.array(n, np.float32), dimensions=3)

        self.vao = Vao()

        self.vao.enable(0)
        self.vao.enable(1)
        self.vao.enable(2)
        self.vao.enable(3)

        self.vao.set_divisor(3, 1)

        self.vao[0] = self.vertex_buffer
        self.vao[1] = self.frag_buffer
        self.vao[2] = self.normals
        self.vao[3] = self.positions


    @ShaderVertex.function
    def main(self):
        self.fragcoord = g.vec2(*self.frag)
        p: g.vec4 = g.vec4(*(self.vetex+self.instance_position), 1)
        self.pixlenormal = (g.vec4(*self.normal, 0) * p).xyz
        self.tolight = (g.vec4(*self.lightp, 0) * p).xyz
        self.gl_Position = p * self.trans *self.projectionmatrix


class MyShader(ShaderFragment):
    def __init__(self):
        ShaderFragment.__init__(self)
        #self.iTime = Uniform[float](float)
        self.textureObj = Uniform[sampler2D](sampler2D)
        self.iResolution = Uniform[g.vec3](g.vec3)
        self.fragcoord = GlslVariable[g.vec2](g.vec2, piping="in")
        self.pixlenormal = GlslVariable[g.vec3](g.vec3, piping="in")
        self.tolight: g.vec3 = GlslVariable[g.vec3](g.vec3, piping="in")

    @ShaderFragment.function
    def main(self):
        gl_FragColor = g.vec4(max(g.dot(g.normalize(self.pixlenormal), g.normalize(self.tolight)), 0.07))


def load_obj(file):
    v = []  # for points on the moddle
    vn = []  # for the normals on the moddle
    f = []  # for the triangles
    with open(file, "r") as fi:
        for line in fi.readlines():
            if line.startswith("v "):
                fu, x, y, z = line.split(" ")
                v.append((float(x), float(z), float(y)))
            elif line.startswith("vn "):
                fu, x, y, z = line.split(" ")
                vn.append((float(x), float(y), float(z)))
            elif line.startswith("f "):
                fu, x, y, z = line.split(" ")
                x = x.split("//")
                y = y.split("//")
                z = z.split("//")
                f.append(((x[0], x[1]),
                          (y[0], y[1]),
                          (z[0], z[1])))
        s = [] # output for corect orderer
        n = []
        for i in f:
            for j in i:
                s.append(v[int(j[0])-1])
                for z in vn[int(j[0])-1]:
                    n.append(z)
    return s, n


def main():
    pygame.init()
    size = (640, 480)
    size = (1000, 1000)
    window = pygame.display.set_mode(size, HWSURFACE | OPENGL | DOUBLEBUF)
    clock = pygame.time.Clock()
    running = True

    output = Texture.from_size(size, internal_format=ss.GL_RGBA)
    #depth = Texture.from_size((640, 480), internal_format=GL_DEPTH_COMPONENT)
    depth = RenderBuffer.from_size(size, internal_format=GL_DEPTH_COMPONENT, multisampling=4)

    p = Program()
    fb = FrameBuffer()
    fb.color = output
    fb.depth = depth
    p.framebuffer = fb
    screen_fb = FrameBuffer.get_default()

    #p.debug = True
    p.options.DEPTH_TEST = True
    p.options.DepthMask = True
    p._target_d = depth

    s = MyShader()
    v = MyVertex()

    p.fragment = s
    p.vertex = v
    p.compile()
    ss.glDepthRange(0.1, 1000)

    tr = glm.mat4(1.0)
    tr = glm.translate(tr, (0, 0, -4))

    rot = tr
    rot = glm.rotate(rot, 3.14159 / 2, (0, 0, 1))
    rot = glm.rotate(rot, 3.14159 / 2, (1, 0, 0))
    rot = glm.rotate(rot, 3.14159 * 1.5, (0, 1, 0))

    v.projectionmatrix = make_matrix(0.1, 1000)
    v.trans = tr.to_list()
    v.lightp = (10, 10, 10)

    while running:
        p.options.DEPTH_TEST = True
        p.options.CULL_FACE = True
        key = pygame.key.get_pressed()
        if key[K_q]:
            tr = glm.translate(tr, (0, 0.5, 0))
        elif key[K_e]:
            tr = glm.translate(tr, (0, -0.5, 0))
        elif key[K_d]:
            tr = glm.translate(tr, (-0.5, 0, 0))
        elif key[K_a]:
            tr = glm.translate(tr, (0.5, 0, 0))
        elif key[K_s]:
            tr = glm.translate(tr, (0, 0, -0.5))
        elif key[K_w]:
            tr = glm.translate(tr, (0, 0, 0.5))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == KEYDOWN:

                if event.key == K_LEFT:
                    rot = glm.rotate(rot, 0.1, (0, 0, 1))
                elif event.key == K_RIGHT:
                    rot = glm.rotate(rot, -0.1, (0, 0, 1))
                elif event.key == K_UP:
                    rot = glm.rotate(rot, 0.1, (0, 1, 0))
                elif event.key == K_DOWN:
                    rot = glm.rotate(rot, -0.1, (0, 1, 0))

        #rot = glm.rotate(rot, 0.05, (0, 0, 1))
        v.trans = (rot * tr).to_list()

        #p.render_vao_indexed(v.vao, v.ebo)
        p.render_instance(v.vao, 1000)

        p.options.DEPTH_TEST = False
        p.options.CULL_FACE = False
        #output.draw_top()
        screen_fb.blit(p.framebuffer, mask=GL_COLOR_BUFFER_BIT)
        pygame.display.flip()
        p.framebuffer.clear()
        clock.tick(20)
    pygame.quit()

main()
