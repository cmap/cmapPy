import unittest
from cmapPy.clue_api_client import setup_logger as setup_logger 
import logging
from cmapPy.clue_api_client import mock_clue_api_client as mock_clue_api_client

__authors__ = "David L. Lahr"
__email__ = "dlahr@broadinstitute.org"


logger = logging.getLogger(setup_logger.LOGGER_NAME)


class TestMockClueApiClient(unittest.TestCase):
    def test_run(self):
        mcao = mock_clue_api_client.MockClueApiClient(default_return_values=[{"hello":"world"}])
        method_list = [mcao.run_filter_query, mcao.run_count_query, mcao.run_delete, mcao.run_post, mcao.run_put]
        for ml in method_list:
            if ml == mcao.run_put:
                r = ml("fake resource name", {"unused":"filter"}, None)
            else:
                r = ml("fake resource name", {"unused":"filter"})
            self.assertIsNotNone(r)
            logger.debug("r:  {}".format(r))
            self.assertEqual(1, len(r))
            r = r[0]
            self.assertEqual(1, len(r))
            self.assertIn("hello", r)
            self.assertEqual("world", r["hello"])


if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()