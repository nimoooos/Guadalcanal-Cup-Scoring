import unittest


class TestCase(unittest.TestCase):
    def test_assertEqual(self):
        # ensures assertEqual is not broken
        self.assertEqual(True, True)

    def test_pivot_self(self):
        from proj_util import pivot_table
        array_2d = [[11, 12, 13, 14], [21, 22, 23, 24], [31, 32, 33, 34]]
        self.assertEqual(array_2d, pivot_table(pivot_table(array_2d)))


if __name__ == '__main__':
    unittest.main()
