import logging
import os
import unittest
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.set_io.grp as grp

logger = logging.getLogger(setup_logger.LOGGER_NAME)
FUNCTIONAL_TESTS_DIR = "functional_tests"


class TestGRP(unittest.TestCase):

	def test_read(self):

		in_grp = grp.read(os.path.join(FUNCTIONAL_TESTS_DIR, "test.grp"))
		self.assertEqual(in_grp, ["r", "d", "e"])

		with self.assertRaises(AssertionError) as e:
			grp.read("testt.grp")
		self.assertIn("The following GRP file", str(e.exception))

	def test_write(self):

		example_grp = ["x", "z", "w"]

		out_path = os.path.join(FUNCTIONAL_TESTS_DIR, "test_write.grp")
		grp.write(example_grp, out_path)
		self.assertTrue(os.path.exists(out_path))

		read_back_in = grp.read(out_path)
		self.assertEqual(example_grp, read_back_in)

		# Cleanup
		os.remove(out_path)

if __name__ == "__main__":
	setup_logger.setup(verbose=True)

	unittest.main()
