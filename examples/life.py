import pygame
from pygame.locals import *

from shader import Shader, fragment, Uniform, hw_flip, Texture
import glsl as g


class MyShader(Shader):
    def __init__(self, t):
        Shader.__init__(self, t)
        self.texture = Uniform(g.sampler2D)

    @fragment
    def main(self):  # this function is called for for each pixel and run on the gpu
        d = g.clamp(g.pow(4.0*d/self.zoom, 0.2), 0.0, 1.0)
        col: g.vec3 = g.vec3(d)
        gl_FragColor = g.vec4(col, 1.0)

def main():
    # pygame stuff
    pygame.init()
    window = pygame.display.set_mode((640, 480), HWSURFACE | OPENGL | DOUBLEBUF)
    pygame.display.set_caption("simple 100% pure python gpu shader")
    clock = pygame.time.Clock()
    running = True
    # make shader object
    output = Texture(window)
    my_shader = MyShader(output)
    my_shader.compile()
    # set up variables for controlling the zoom and drag to move
    z = 80  # the zoom level
    scroll_speed = 80
    pos = pygame.Vector2(0, 0)
    rel = (0, 0)  # distance the mouse moved while the mouse button is down
    start = None
    zoo = pow(0.5, 32.0 * (0.5 - 0.5 * (z / scroll_speed)))  # normalized zoom
    my_shader.zoom = zoo
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    start = pygame.mouse.get_pos()
                if event.button == 5:
                    z = min(z+1, 90)
                elif event.button == 4:
                    z = max(0, z-1)  # cap the zoom level
                my_shader.zoom = zoo

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    pos.x += rel[0]
                    pos.y += rel[1]
                    rel = (0, 0)
                    start = None

        zoo: float = pow(0.5, 32.0 * (0.5 - 0.5 * (z / scroll_speed)))
        if start:
            m = pygame.mouse.get_pos()
            rel = start[0] - m[0], start[1] - m[1]
            rel = rel[0] / (window.get_size()[0] / 2), rel[1] / (window.get_size()[1] / -2)
            rel = (rel[0] * zoo, rel[1] * zoo)

        my_shader.zoom_pos = pos.x+rel[0], pos.y+rel[1]  # +rel for update position mid drag
        my_shader.render()
        window.blit(output.get_surface(), (0, 0))
        hw_flip()  # pygame doesnt not like "HWSURFACE | OPENGL" but its required for shader
        # so we need to call this so we can use a shader and all the normal pygame stuff
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
