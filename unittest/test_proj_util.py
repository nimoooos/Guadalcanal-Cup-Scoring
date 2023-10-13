import unittest
import logging
from proj_util import now_hst, random_code

test_code = random_code(5)
logging.basicConfig(level=logging.DEBUG,
                    format='{code} - {time} - %(levelname)s: %(message)s'.format(code=test_code, time=now_hst("string")),
                    filename="unittest.log", filemode='a')


class TestCasePivotTable(unittest.TestCase):
    def test_pivot(self):
        logging.info("test_pivot() initialized.")
        from proj_util import pivot_table
        array_23 = [[11, 12, 13], [21, 22, 23]]
        array_23_pivot = [[11, 21], [12, 22], [13, 23]]
        logging.debug("Testing if pivot works properly.")
        self.assertEqual(array_23, pivot_table(array_23_pivot))
        logging.debug("Testing if double pivot works properly.")
        self.assertEqual(array_23, pivot_table(pivot_table(array_23)))
        logging.info("test_pivot() completed.")


class TestCaseRandomCode(unittest.TestCase):
    def test_randomness(self):
        logging.info("test_randomness() initialized.")
        from proj_util import random_code
        code_list = []
        logging.debug("Generating a random 6 digit code.")
        code = random_code(6)
        logging.debug("The code is "+code)
        logging.debug("Generating a large list of random codes.")
        for i in range(65536):
            code_list.append(random_code(6))
        self.assertNotIn(code, code_list)
        logging.info("test_randomness() completed.")


class TestCaseWriteCSV(unittest.TestCase):
    def setUp(self):
        logging.info("setUp() called.")
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
        logging.info("tearDown() called.")
        import os
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

    def test_write(self):
        """
        Checks if the file was written
        """
        logging.info("test_write() initialized.")
        from os import path
        file_exists = path.isfile(self.filepath)
        self.assertTrue(file_exists)
        logging.info("test_write() completed.")

    def test_read(self):
        logging.info("test_read() initialized.")
        file = open(self.filepath, "r")
        file_string = file.read()
        self.assertEqual("11,12,13,14\n21,22,23,24\n31,32,33,34\n", file_string)
        file.close()
        logging.info("test_read() completed.")


if __name__ == '__main__':
    unittest.main()
