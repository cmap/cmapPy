import unittest
from cmapPy.clue_api_client import setup_logger as setup_logger
import logging
import test_clue_api_client
from cmapPy.clue_api_client import cell_queries as cq

__authors__ = "David L. Lahr"
__email__ = "dlahr@broadinstitute.org"


logger = logging.getLogger(setup_logger.LOGGER_NAME)

cao = None


class TestCellQueries(unittest.TestCase):
    def test_is_cell_line_in_api(self):
        r = cq.is_cell_line_in_api(cao, "A375")
        self.assertTrue(r)
        r = cq.is_cell_line_in_api(cao, "Dave Lahr's fake cell line that never existed")
        self.assertFalse(r)


if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    cao = test_clue_api_client.build_clue_api_client_from_default_test_config()

    unittest.main()