import unittest
from cmapPy.clue_api_client import setup_logger as setup_logger
import logging
import test_clue_api_client
from cmapPy.clue_api_client import pert_queries as pq

__authors__ = "David L. Lahr"
__email__ = "dlahr@broadinstitute.org"


logger = logging.getLogger(setup_logger.LOGGER_NAME)

cao = None


class TestPertQueries(unittest.TestCase):
    def test__build_map_from_clue_api_result(self):
        r = pq._build_map_from_clue_api_result([{"a": "b", "c": "d"}], "a", "c")
        self.assertIsNotNone(r)
        logger.debug("r:  {}".format(r))
        self.assertEquals(1, len(r))
        self.assertIn("b", r)
        self.assertEquals("d", r["b"])

    def test_retrieve_pert_id_pert_iname_map(self):
        r = pq.retrieve_pert_id_pert_iname_map(["BRD-K21680192", "BRD-K88378636", "not a valid BRD"], cao)
        self.assertIsNotNone(r)
        logger.debug("r:  {}".format(r))
        self.assertEqual(2, len(r))
        self.assertIn("BRD-K21680192", r)
        self.assertIsNotNone(r["BRD-K21680192"])
        self.assertIn("BRD-K88378636", r)
        self.assertIsNotNone(r["BRD-K88378636"])
        self.assertNotIn("not a valid BRD", r)

    def test_retrieve_pert_id_pert_type_map(self):
        r = pq.retrieve_pert_id_pert_type_map(["BRD-K21680192", "BRD-K88378636", "not a valid BRD"], cao)
        self.assertIsNotNone(r)
        logger.debug("r:  {}".format(r))
        self.assertEqual(2, len(r))
        self.assertIn("BRD-K21680192", r)
        self.assertIsNotNone(r["BRD-K21680192"])
        self.assertIn("BRD-K88378636", r)
        self.assertIsNotNone(r["BRD-K88378636"])
        self.assertNotIn("not a valid BRD", r)


if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    cao = test_clue_api_client.build_clue_api_client_from_default_test_config()

    unittest.main()