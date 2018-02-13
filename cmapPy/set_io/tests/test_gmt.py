import logging
import os
import unittest
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.set_io.gmt as gmt

logger = logging.getLogger(setup_logger.LOGGER_NAME)
FUNCTIONAL_TESTS_DIR = "functional_tests"


class TestGMT(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.example_gmt = [{"head": "A", "desc": "this one is A", "entry": ["a1", "a3", "a2"]},
		                   {"head": "B", "desc": "this one is B", "entry": ["b4", "b2", "b3"]}]

	def test_read(self):

		in_gmt = gmt.read(os.path.join(FUNCTIONAL_TESTS_DIR, "test.gmt"))

		self.assertEqual(len(self.example_gmt), len(in_gmt))
		self.assertEqual(self.example_gmt[0], in_gmt[0])
		self.assertEqual(self.example_gmt[1], in_gmt[1])

		with self.assertRaises(AssertionError) as e:
			gmt.read(os.path.join(FUNCTIONAL_TESTS_DIR, "test_bad.gmt"))
		self.assertIn("3 tab-delimited items. line_num: 0", str(e.exception))

		with self.assertRaises(AssertionError) as e:
			gmt.read(os.path.join(FUNCTIONAL_TESTS_DIR, "test_bad2.gmt"))
		self.assertIn("same set. line_num: 1", str(e.exception))

	def test_verify_gmt_integrity(self):

		bad_gmt = [{"head": "A", "desc": "blah", "entry": ["a1", "a3", "a2"]},
		           {"head": "A", "desc": "blah", "entry": ["b4", "b2", "b3"]}]

		with self.assertRaises(AssertionError) as e:
			gmt.verify_gmt_integrity(bad_gmt)
		self.assertIn("Set identifiers should be unique", str(e.exception))

	def test_write(self):

		out_path = os.path.join(FUNCTIONAL_TESTS_DIR, "test_write.gmt")
		gmt.write(self.example_gmt, out_path)
		self.assertTrue(os.path.exists(out_path))

		read_back_in = gmt.read(out_path)
		self.assertEqual(len(self.example_gmt), len(read_back_in))
		self.assertEqual(self.example_gmt[0], read_back_in[0])
		self.assertEqual(self.example_gmt[1], read_back_in[1])

		# Cleanup
		os.remove(out_path)

if __name__ == "__main__":
	setup_logger.setup(verbose=True)

	unittest.main()
