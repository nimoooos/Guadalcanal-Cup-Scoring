import unittest


class TestCasePivotTable(unittest.TestCase):
    def test_pivot(self):
        from proj_util import pivot_table
        array_23 = [[11, 12, 13], [21, 22, 23]]
        array_23_pivot = [[11, 21], [12, 22], [13, 23]]
        self.assertEqual(array_23, pivot_table(array_23_pivot))
        self.assertEqual(array_23, pivot_table(pivot_table(array_23)))


class TestCaseRandomCode(unittest.TestCase):
    def test_randomness(self):
        from proj_util import random_code
        code_list = []
        code = random_code(6)
        for i in range(65536):
            code_list.append(random_code(6))
        self.assertNotIn(code, code_list)


if __name__ == '__main__':
    unittest.main()
