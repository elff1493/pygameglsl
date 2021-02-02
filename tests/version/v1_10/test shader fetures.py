import unittest
import shader
import pygame

class TestShader1_10(unittest.TestCase):
    def setUp(self):
        pygame.init()
        window = pygame.display.set_mode((640, 480), pygame.HWSURFACE | pygame.OPENGL | pygame.DOUBLEBUF)
        self.texture = shader.Texture(window)
        self.shader = shader.Shader(self.texture)

    def tearDown(self):
        pygame.quit()

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

if __name__ == "__main__":
    t = TestShader1_10()
    t.main()
