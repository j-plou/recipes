import unittest

from main import Main


class TestMain(unittest.TestCase):
    def test_hy(self):
        main = Main()
        self.assertEqual(main.say_hi("Paco"), "Hi, Paco")


if __name__ == "__main__":
    unittest.main()
