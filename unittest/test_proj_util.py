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


class TestCaseWriteCSV(unittest.TestCase):
    def setUp(self):
        from proj_util import write_to_csv
        import os
        self.directory = os.path.join("testfiles")
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        self.array_34 = [[11, 12, 13, 14], [21, 22, 23, 24], [31, 32, 33, 34]]
        self.filename = "CSV_test_write.csv"
        self.filepath = os.path.join(self.directory, self.filename)

        write_to_csv(self.directory, self.filename, self.array_34)

    def tearDown(self):
        import os
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

    def test_write(self):
        """
        Checks if the file was written
        """
        from os import path
        file_exists = path.isfile(self.filepath)
        self.assertTrue(file_exists)

    def test_read(self):
        file = open(self.filepath, "r")
        file_string = file.read()
        self.assertEqual("11,12,13,14\n21,22,23,24\n31,32,33,34\n", file_string)
        file.close()


if __name__ == '__main__':
    unittest.main()
