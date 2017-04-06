import unittest
from cmapPy.clue_api_client import setup_logger
import logging
import test_clue_api_client
from cmapPy.clue_api_client import macchiato_queries as mq

__authors__ = "David L. Lahr"
__email__ = "dlahr@broadinstitute.org"


logger = logging.getLogger(setup_logger.LOGGER_NAME)

cao = None

test_brew_prefix = "test_brew_prefix_for_test_macchiato_queries"
test_status = "test macchiato status for test_macchiato_queries"


class TestMacchiatoQueries(unittest.TestCase):
    def setUp(self):
        test_clue_api_client.add_entry_if_not_already_present(cao, mq.resource_name,
            {"brew_prefix":test_brew_prefix}, {"brew_prefix":test_brew_prefix, "status": test_status})

    def test_is_brew_prefix_in_api(self):
        r = mq.is_brew_prefix_in_api(cao, test_brew_prefix)
        self.assertTrue(r)

        r = mq.is_brew_prefix_in_api(cao, "Dave Lahr's fake brew prefix that hopefully will never exist in the API")
        self.assertFalse(r)

    def test_get_api_id(self):
        r = mq.get_api_id(cao, test_brew_prefix)
        self.assertIsNotNone(r)
        logger.debug("r:  {}".format(r))

    def test_change_status(self):
        cur_id = mq.get_api_id(cao, test_brew_prefix)

        expected_new_status = "test status for test_macchiato_queries TestMacchiatoQueries.test_change_status"
        r = mq.change_status(cao, cur_id, expected_new_status)
        self.assertIsNotNone(r)
        logger.debug("r:  {}".format(r))
        self.assertIn("status", r)
        self.assertEqual(expected_new_status, r["status"])

    def test_create_brew_prefix_in_api(self):
        #happy path
        expected_brew_prefix = "brew_prefix for TestMacchiatoQueries.test_create_brew_prefix_in_api"
        r = mq.create_brew_prefix_in_api(cao, expected_brew_prefix, status=test_status)
        self.assertIsNotNone(r)
        logger.debug("r:  {}".format(r))
        self.assertIn("id", r)
        self.assertIsNotNone(r["id"])

        #cleanup by deleting created entry
        cao.run_delete(mq.resource_name, r["id"])


if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    cao = test_clue_api_client.build_clue_api_client_from_default_test_config()

    unittest.main()