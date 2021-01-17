import pygame
from pygame.locals import *

from shader import fragment, Uniform, Texture, ShaderFragment, ShaderVertex, Vao, Program, Attribute, Vbo, \
    vertex, GlslVariable, Ebo, GL_DEPTH_COMPONENT
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
        ShaderVertex.__init__(self, Vao())
        self.vetex = Attribute(g.vec3, 0)
        self.frag = Attribute(g.vec2, 1)
        self.normal = Attribute(g.vec3, 2)
        self.iTime = Uniform(float)
        self.projectionmatrix = Uniform(g.mat4)
        self.trans = Uniform(g.mat4)
        self.fragcoord = GlslVariable(g.vec2, piping="out")
        self.pixlenormal = GlslVariable(g.vec3, piping="out")
        self.tolight = GlslVariable(g.vec3, piping="out")
        self.lightp = Uniform(g.vec3)
        #self.fragnormal = GlslVariable(g.vec3, piping="out")
        self.vertex_buffer = Vbo()
        self.frag_buffer = Vbo()
        self.normals = Vbo()
        self.ebo = Ebo()

        b, n = load_obj("bunny.obj")
        bunny = np.array(b,  np.float32)

        self.ebo.set_data(np.array([i for i in range(len(b))],  np.uintc), dimensions=2)
        self.vertex_buffer.set_data(bunny, dimensions=3)
        self.frag_buffer.set_data(np.array([1 for i in range(2*len(b))],  np.uintc), dimensions=2)

        self.normals.set_data(np.array(n, np.float32), dimensions=3)

        self.vao[0] = self.vertex_buffer
        self.vao[1] = self.frag_buffer
        self.vao[2] = self.normals
        self.vao.enable(0)
        self.vao.enable(1)
        self.vao.enable(2)

    @ShaderVertex.function
    def main(self):
        self.fragcoord = self.frag
        p: g.vec4 = g.vec4(self.vetex, 1) * self.trans
        self.pixlenormal = (g.vec4(self.normal, 0) * p).xyz
        self.tolight = (g.vec4(self.lightp, 0) * p).xyz
        gl_Position = p * self.projectionmatrix


class MyShader(ShaderFragment):
    def __init__(self, t):
        ShaderFragment.__init__(self, t)
        self.iTime: float = Uniform(float)
        self.textureObj = Uniform(sampler2D)
        self.iResolution = Uniform(g.vec3)
        self.fragcoord = GlslVariable(g.vec2, piping="in")
        self.pixlenormal = GlslVariable(g.vec3, piping="in")
        self.tolight = GlslVariable(g.vec3, piping="in")

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
    window = pygame.display.set_mode((640, 480), HWSURFACE | OPENGL | DOUBLEBUF)
    clock = pygame.time.Clock()
    running = True

    output = Texture.from_size((640, 480), internal_format=ss.GL_RGBA)
    depth = Texture.from_size((640, 480), internal_format=GL_DEPTH_COMPONENT)

    p = Program()

    p.debug = True
    p.options.DEPTH_TEST = True
    p.options.DepthMask = True
    p._target_d = depth

    s = MyShader(output)
    v = MyVertex()

    p.fragment = s
    p.vertex = v
    p.compile()
    ss.glDepthRange(0.1, 1000)

    tr = glm.mat4(1.0)
    tr = glm.translate(tr, (0, 0, -4))

    rot = glm.mat4(1.0)
    rot = glm.rotate(rot, 3.14159 / 2, (0, 0, 1))
    rot = glm.rotate(rot, 3.14159 / 2, (1, 0, 0))
    rot = glm.rotate(rot, 3.14159 * 1.5, (0, 1, 0))

    v.projectionmatrix = make_matrix(0.1, 1000)
    v.trans = tr.to_list()
    v.lightp = (10, 10, 10)

    while running:
        p.options.DEPTH_TEST = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    tr = glm.translate(tr, (0, 0.1, 0))
                elif event.key == K_e:
                    tr = glm.translate(tr, (0, -0.1, 0))
                elif event.key == K_d:
                    tr = glm.translate(tr, (-0.1, 0, 0))
                elif event.key == K_a:
                    tr = glm.translate(tr, (0.1, 0, 0))
                elif event.key == K_s:
                    tr = glm.translate(tr, (0, 0, -0.1))
                elif event.key == K_w:
                    tr = glm.translate(tr, (0, 0, 0.1))
                elif event.key == K_LEFT:
                    rot = glm.rotate(rot, 0.1, (0, 0, 1))
                elif event.key == K_RIGHT:
                    rot = glm.rotate(rot, -0.1, (0, 0, 1))
                elif event.key == K_UP:
                    rot = glm.rotate(rot, 0.1, (0, 1, 0))
                elif event.key == K_DOWN:
                    rot = glm.rotate(rot, -0.1, (0, 1, 0))

        rot = glm.rotate(rot, 0.1, (0, 0, 1))

        v.trans = (tr * rot).to_list()

        p.render_vao_indexed(v.ebo)

        p.options.DEPTH_TEST = False
        output.draw_top()
        pygame.display.flip()
        p.clear()
        clock.tick(30)
    pygame.quit()

main()
