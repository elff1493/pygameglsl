import pygame
from pygame.locals import *

from shader import Shader, fragment, Uniform, Texture, NEAREST
import glsl as g
import random

class MyShader(Shader):
    def __init__(self, t):
        Shader.__init__(self, t)
        self.texture = Uniform(g.sampler2D)
        self.size = Uniform(g.vec2)

    @fragment
    def cell(self, p: g.vec2) -> int: # gets the value of a cell
        p = p/self.size
        p = g.fract(p+1)
        return int(g.texture2D(self.texture, p).x)

    @fragment
    def main(self):  # this function is called for for each pixel and run on the gpu
        px: g.vec2 = g.ivec2(self.fragCoord * self.size)
        px += 0.5  # just need to move half a pixle over so we sample the middle
        k: int = self.cell(px + g.ivec2(-1, -1)) + self.cell(px + g.ivec2(0, -1))
        k += self.cell(px + g.ivec2(1, -1)) + self.cell(px + g.ivec2(-1, 0)) + self.cell(px + g.ivec2(1, 0))
        k += self.cell(px + g.ivec2(-1, 1)) + self.cell(px + g.ivec2(0, 1)) + self.cell(px + g.ivec2(1, 1))
        e: int = self.cell(px)
        f: float = float((k == 2 and e == 1) or (k == 3))
        gl_FragColor = g.vec4(f, f, f, 1.0)


# pygame stuff
pygame.init()
window = pygame.display.set_mode((1000, 1000), HWSURFACE | OPENGL | DOUBLEBUF)
pygame.display.set_caption("game of life on gpu")
running = True

# set random start
for x in range(window.get_width()):
    for y in range(window.get_height()):
        r = random.choice([255, 0])
        window.set_at((x, y), (r, r, r))

# setup shader stuff
output = Texture(window, filter=NEAREST)

my_shader = MyShader(output)
my_shader.compile()
my_shader.size = window.get_size()
my_shader.texture = output  # pass the render target in to the shader so we can see last frame
while running:
    t = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    my_shader.render()  # shader code called here
    output.draw_top()  # this is hardware draw call, faster than getting the surface then bliting to the screen
    pygame.display.flip()
    print("time (millisecond): ", pygame.time.get_ticks() - t)

pygame.quit()

