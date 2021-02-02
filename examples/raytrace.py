import pygame
from pygame.locals import *

from shader import Shader, fragment, Uniform, Texture, NEAREST, hw_flip, GlslVariable, OUT, IN
import glsl as g
import random


class MyShader(Shader):
    def __init__(self, t):
        Shader.__init__(self, t)



# pygame stuff
pygame.init()
window = pygame.display.set_mode((1000, 1000), HWSURFACE | OPENGL | DOUBLEBUF)
pygame.display.set_caption("game of life on gpu")
running = True



# setup shader stuff
output = Texture.from_surface(window)
output.set_filter(NEAREST)
output2 = output
output2.set_active(1)
my_shader = MyShader(output)
my_shader.compile()
my_shader.size = window.get_size()
my_shader.texture = output2  # pass the render target in to the shader so we can see last frame
clock = pygame.time.Clock()
while running:
    t = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    my_shader.render()  # shader code called here
    #output.draw_top()  # this is hardware draw call, faster than getting the surface then bliting to the screen
    window.blit(output.get_surface(), (0, 0))
    hw_flip()
    pygame.display.flip()


pygame.quit()

