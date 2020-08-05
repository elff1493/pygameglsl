import unittest
import decomp

class TestShader1_10(unittest.TestCase):
    def setUp(self):
        self.decomp = decomp.Recompiler()

    def tearDown(self):
        pygame.quit()

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

if __name__ == "__main__":
    t = TestShader1_10()
    t.main()