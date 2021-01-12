import pygame
from pygame.locals import *
from shader import fragment, Uniform, hw_flip, Texture, ShaderFragment, ShaderVertex, Vao, Program, Attribute, Vbo, \
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
        self.iTime = Uniform(float)
        self.projectionmatrix = Uniform(g.mat4)
        self.trans = Uniform(g.mat4)
        self.fragcoord = GlslVariable(g.vec2, piping="out")
        self.vertex_buffer = Vbo()
        self.frag_buffer = Vbo()
        self.ebo = Ebo()
        # ebodata = np.array([0, 1, 2, 1, 2, 3], np.uintc)

        # tdata = np.array([[0, 0], [1, 0], [0, 1], [1, 1]
        # ], np.float32)
        # vdata = np.array([[-0.5, -0.5, -1], [0.5, -0.5, -1],
        # [-0.5, 0.5, -1], [0.5, 0.5, -1]
        # ], np.float32)
        ebodata = np.array([
            0, 1, 3,
            3, 1, 2,
            4, 5, 7,
            7, 5, 6,
            8, 9, 11,
            11, 9, 10,
            12, 13, 15,
            15, 13, 14,
            16, 17, 19,
            19, 17, 18,
            20, 21, 23,
            23, 21, 22], np.uintc)

        tdata = np.array([0, 0,
                          0, 1,
                          1, 1,
                          1, 0,
                          0, 0,
                          0, 1,
                          1, 1,
                          1, 0,
                          0, 0,
                          0, 1,
                          1, 1,
                          1, 0,
                          0, 0,
                          0, 1,
                          1, 1,
                          1, 0,
                          0, 0,
                          0, 1,
                          1, 1,
                          1, 0,
                          0, 0,
                          0, 1,
                          1, 1,
                          1, 0
                          ], np.intc)
        vdata = np.array([-0.5, 0.5, -0.5,
                          -0.5, -0.5, -0.5,
                          0.5, -0.5, -0.5,
                          0.5, 0.5, -0.5,

                          -0.5, 0.5, 0.5,
                          -0.5, -0.5, 0.5,
                          0.5, -0.5, 0.5,
                          0.5, 0.5, 0.5,

                          0.5, 0.5, -0.5,
                          0.5, -0.5, -0.5,
                          0.5, -0.5, 0.5,
                          0.5, 0.5, 0.5,

                          -0.5, 0.5, -0.5,
                          -0.5, -0.5, -0.5,
                          -0.5, -0.5, 0.5,
                          -0.5, 0.5, 0.5,

                          -0.5, 0.5, 0.5,
                          -0.5, 0.5, -0.5,
                          0.5, 0.5, -0.5,
                          0.5, 0.5, 0.5,

                          -0.5, -0.5, 0.5,
                          -0.5, -0.5, -0.5,
                          0.5, -0.5, -0.5,
                          0.5, -0.5, 0.5
                          ], np.float32)

        self.ebo.set_data(ebodata, dimensions=2)
        self.vertex_buffer.set_data(vdata, dimensions=3)
        self.frag_buffer.set_data(tdata, dimensions=3)

        self.vao[0] = self.vertex_buffer
        self.vao[1] = self.frag_buffer
        self.vao.enable(0)
        self.vao.enable(1)

    @vertex
    def main(self):
        self.fragcoord = self.frag
        gl_Position = g.vec4(self.vetex, 1) * self.trans * self.projectionmatrix


class MyShader(ShaderFragment):
    def __init__(self, t):
        ShaderFragment.__init__(self, t)
        self.iTime: float = Uniform(float)
        self.textureObj = Uniform(sampler2D)
        self.iResolution = Uniform(g.vec3)
        self.fragcoord = GlslVariable(g.vec2, piping="in")

    @fragment
    def get_p(self, p: g.vec2) -> g.vec2:
        return abs(p) / g.dot(p, p) - 0.63

    @fragment
    def main(self):
        p: g.vec2 = 2. * self.fragcoord
        p *= 4
        p = g.mod(p, 4.0) - 2.0

        for i in range(0, 4):
            p = self.get_p(p)  # abs(p) / _gl.dot(p, p) - 0.63
            p *= 2.0
        p = p / 2.0
        de: float = abs(g.dot(p, g.vec2(g.cos(self.iTime), g.sin(self.iTime))))
        gl_FragColor = g.vec4(g.vec3(de), 1.0)
        gl_FragColor = g.texture2D(self.textureObj, self.fragcoord)
        gl_FragColor = g.vec4(self.fragcoord, 0, 0)
        # gl_FragColor.r = (g.sin(self.iTime)+1)/2


def main():
    pygame.init()
    window = pygame.display.set_mode((640, 480), HWSURFACE | OPENGL | DOUBLEBUF)
    img = pygame.image.load("alien1.jpg")
    # img = pygame.transform.scale(img)
    output = Texture()
    output.tex = 0
    output.set_surface(window)
    #output = Texture.from_size((640, 480), internal_format=ss.GL_RGBA)
    #output.tex = 0
    output.width = 480
    output.height = 640
    depth = Texture.from_size((640, 480), internal_format=GL_DEPTH_COMPONENT)
    t = Texture.from_surface(img)
    t.set_active(1)

    p = Program()
    p.debug = True
    p.options.DEPTH_TEST = True
    p.options.ALPHA_TEST = False
    p.options.DepthMask = True
    p.options.ClearDepth = 0.5
    p.options.DepthFunc = ss.GL_ALWAYS
    s = MyShader(output)
    v = MyVertex()
    p._target_d = depth
    p.fragment = s
    p.vertex = v
    p.compile()
    s.textureObj = t
    v.projectionmatrix = make_matrix(0.1, 1000)
    ss.glDepthRange(0.1, 1000)
    tr = glm.mat4(1.0)
    rot = glm.mat4(1.0)

    # glm.rotate(t)
    tr = glm.translate(tr, (0, 0, -4))
    print(tr)
    v.trans = tr.to_list()
    clock = pygame.time.Clock()
    running = True
    # screen = Texture(window)

    while running:
        p.options.DEPTH_TEST = True
        p.options.DepthMask = True
        p.options.DepthFunc = ss.GL_ALWAYS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == KEYDOWN:
                # tr = glm.translate(tr, (-1, -1, 0))

                print(tr)
                print()
                if event.key == K_w:
                    tr = glm.translate(tr, (0, 0.01, 0))
                elif event.key == K_s:
                    tr = glm.translate(tr, (0, -0.01, 0))
                elif event.key == K_a:
                    tr = glm.translate(tr, (-0.01, 0, 0))
                elif event.key == K_d:
                    tr = glm.translate(tr, (0.01, 0, 0))

                elif event.key == K_q:
                    tr = glm.translate(tr, (0, 0, -0.1))
                elif event.key == K_e:
                    tr = glm.translate(tr, (0, 0, 0.1))
                elif event.key == K_LEFT:
                    rot = glm.rotate(rot, 0.1, (0, 0, 1))
                elif event.key == K_RIGHT:
                    rot = glm.rotate(rot, -0.1, (0, 0, 1))
                elif event.key == K_UP:
                    rot = glm.rotate(rot, 0.1, (0, 1, 0))
                elif event.key == K_DOWN:
                    rot = glm.rotate(rot, -0.1, (0, 1, 0))

        s.iTime = pygame.time.get_ticks() / 1000
        v.trans = (tr * rot).to_list()
        p.render_vao_indexed(v.ebo)

        #window.blit(t.get_surface(), pygame.mouse.get_pos())
        #window.blit(output.get_surface(), (0, 0))




        hw_flip()
        #p.options.DepthMask = False
        if pygame.key.get_pressed()[K_SPACE]:
            depth.draw_top()
        #p.options.DepthMask = False
        pygame.display.flip()
        p.options.DepthMask = True
        p.clear()
        clock.tick(30)
        #p.cleard()
    pygame.quit()


main()
