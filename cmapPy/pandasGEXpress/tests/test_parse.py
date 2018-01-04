import sys
sys.path.insert(0, "../../..")
import logging
from cmapPy.pandasGEXpress import setup_GCToo_logger as setup_logger
import unittest
import pandas.util.testing as pandas_testing
from cmapPy.pandasGEXpress import GCToo as GCToo 
from cmapPy.pandasGEXpress import parse_gctx as parse_gctx
from cmapPy.pandasGEXpress import mini_gctoo_for_testing as mini_gctoo_for_testing

__author__ = "Oana Enache"
__email__ = "oana@broadinstitute.org"

logger = logging.getLogger(setup_logger.LOGGER_NAME)

class TestParse(unittest.TestCase):
	def test_gctx_parsing(self):
		pass

	def test_gct_parsing(self):
		pass
