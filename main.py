import pygame
from pygame.locals import *
from shader import Shader, fragment, Uniform, hw_flip, Texture
from glsl.v1_10 import sampler2D
from glsl import v1_10 as g


class MyShader(Shader):
    def __init__(self, t):
        Shader.__init__(self, t)
        self.iTime: float = Uniform(float)
        self.textureObj = Uniform(sampler2D)
        self.iResolution = Uniform(g.vec3)

    @fragment
    def test(self) -> None:
        a = 1 + self
        if 1 or 2 and 3:
            a = 1
        a[1] = 1
        #ass list
        #ass name?
        #ass typle
        assert 1 == 1
        #assing
        a: int = 1
        #backquote
        a = a & 1
        a = a | 1
        a = a ^ 1
        a = call()
        #class
        a = 1==4
        a = 5
        #decorator
        a = {}
        # elipsis/ sliceing
        # Expression
        # Exec
        # FloorDiv
        for i in range(5):
            if i:
                break
            continue
        def f():
            return 1
        a = a.atter
        global aa
        if 1:
            a = 1
        a = not a
        # keyword
        # Lambda
        # LeftShift
        # List
        # ListComp
        # ListCompFor
        # ListCompIf
        # Mod
        a = a % 3
        a = a * 1
        a = not a
        a = a ** a


    @fragment
    def get_p(self, p:g.vec2) -> g.vec2:
        return abs(p) / g.dot(p, p) - 0.63

    @fragment
    def main(self):
        p: g.vec2 = 2. * self.fragCoord
        p *= 4
        p = g.mod(p, 4.0) - 2.0

        for i in range(0, 4):
            p = self.get_p(p)#abs(p) / _gl.dot(p, p) - 0.63
            p *= 2.0
        p = p / 2.0
        de: float = abs(g.dot(p, g.vec2(g.cos(self.iTime), g.sin(self.iTime))))
        gl_FragColor = g.vec4(g.vec3(de), 1.0)
        gl_FragColor = g.texture2D(self.textureObj, self.fragCoord)
        gl_FragColor.r = (g.sin(self.iTime)+1)/2

def main():
    pygame.init()
    window = pygame.display.set_mode((640, 480), HWSURFACE | OPENGL | DOUBLEBUF)
    img = pygame.image.load("alien1.jpg")
    img = pygame.transform.scale(img, (128, 128))
    output = Texture(img)
    s = MyShader(output)

    t = Texture(img)
    s.compile()
    s.tex = t.tex
    clock = pygame.time.Clock()
    running = True
    #e = T(1)
    s.textureObj = t
    #screen = Texture(window)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        #glClearColor(0.25, 0.25, 0.25, 1)
        #glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        s.iTime = pygame.time.get_ticks()/1000

        s.render()

        #window.fill((255, 0, 0))
        window.blit(t.get_surface(), pygame.mouse.get_pos())
        window.blit(output.get_surface(), (0, 0))

        clock.tick(60)
        hw_flip()
        #screen.set_surface(window)
        #screen.draw_top()
        pygame.display.flip()
    pygame.quit()
main()