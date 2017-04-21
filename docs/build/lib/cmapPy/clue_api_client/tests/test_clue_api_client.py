import unittest
from cmapPy.clue_api_client import setup_logger as setup_logger
import logging
from cmapPy.clue_api_client import clue_api_client as clue_api_client
import os.path
import ConfigParser
import collections

__authors__ = "David L. Lahr"
__email__ = "dlahr@broadinstitute.org"


logger = logging.getLogger(setup_logger.LOGGER_NAME)

config_filepath = os.path.expanduser("~/.l1ktools_python.cfg")
config_section = "test"
cao = None

test_brew_prefix = "dlahr brew prefix 001"
test_status = "my fake status"

class TestClueApiClient(unittest.TestCase):
    def test_run_query(self):
        #get one gene
        r = cao.run_filter_query("genes", {"where":{"pr_gene_id":5720}})
        self.assertIsNotNone(r)
        logger.debug("len(r):  {}".format(len(r)))
        logger.debug("r:  {}".format(r))
        self.assertEqual(1, len(r))

        #get multiple genes
        r = cao.run_filter_query("genes", {"where":{"pr_gene_id":{"inq":[5720,207]}}})
        self.assertIsNotNone(r)
        logger.debug("len(r):  {}".format(len(r)))
        logger.debug("r:  {}".format(r))
        self.assertEqual(2, len(r))

        r = cao.run_filter_query("perts", {"where":{"pert_id":"BRD-K12345678"}})
        self.assertIsNotNone(r)
        logger.debug("len(r):  {}".format(len(r)))
        self.assertEqual(0, len(r))

    def test_run_query_handle_fail(self):
        with self.assertRaises(Exception) as context:
            cao.run_filter_query("fakeresource", {})
        self.assertIsNotNone(context.exception)
        logger.debug("context.exception:  {}".format(context.exception))
        self.assertIn("ClueApiClient request failed", str(context.exception))

    def test_run_where_query(self):
        r = cao.run_count_query("cells", {"cell_id":"A375"})
        self.assertIsNotNone(r)
        logger.debug("r:  {}".format(r))
        self.assertIn("count", r)
        self.assertEqual(1, r["count"])

    def test__check_request_response(self):
        FakeResponse = collections.namedtuple("FakeResponse", ["status_code", "reason"])

        #happy path
        fr = FakeResponse(200, None)
        clue_api_client.ClueApiClient._check_request_response(fr)

        #response status code that should cause failure
        fr2 = FakeResponse(404, "I don't need a good reason!")
        with self.assertRaises(Exception) as context:
            clue_api_client.ClueApiClient._check_request_response(fr2)
        logger.debug("context.exception:  {}".format(context.exception))
        self.assertIn(str(fr2.status_code), str(context.exception))
        self.assertIn(fr2.reason, str(context.exception))

    def test_run_post(self):
        #check that the entry isn't already there, if it is delete it
        check_result = cao.run_count_query("macchiato", {"brew_prefix":test_brew_prefix})
        if check_result["count"] == 1:
            lookup_result = cao.run_filter_query("macchiato", {"where":{"brew_prefix":test_brew_prefix}})[0]
            cao.run_delete("macchiato", lookup_result["id"])

        #happy path
        data = {"brew_prefix":test_brew_prefix, "status":test_status}
        r = cao.run_post("macchiato", data)
        self.assertIsNotNone(r)
        logger.debug("r:  {}".format(r))
        self.assertIn("brew_prefix", r)
        self.assertEqual(data["brew_prefix"], r["brew_prefix"])
        self.assertIn("id", r)
        #check that user key has not been added to entry
        self.assertNotIn("user_key", r)

        #clean up
        r = cao.run_delete("macchiato", r["id"])

    def test_run_delete(self):
        #check that there is an entry to delete, if not create it
        lookup_result = add_entry_if_not_already_present(cao, "macchiato", {"brew_prefix":test_brew_prefix},
                                         {"brew_prefix":test_brew_prefix, "status": test_status})

        delete_id = lookup_result["id"]

        #happy path
        r = cao.run_delete("macchiato", delete_id)
        self.assertIsNotNone(r)
        logger.debug("r:  {}".format(r))
        self.assertTrue(r)

    def test_run_put(self):
        #check that there is an entry to update, if not create it
        lookup_result = add_entry_if_not_already_present(cao, "macchiato", {"brew_prefix":test_brew_prefix},
                                         {"brew_prefix":test_brew_prefix, "status": test_status})

        put_id = lookup_result["id"]

        expected_status = "test status for test_clue_api_client test_run_put"
        r = cao.run_put("macchiato", put_id, {"status":expected_status})
        self.assertIsNotNone(r)
        logger.debug("r:  {}".format(r))
        self.assertIn("status", r)
        self.assertEqual(expected_status, r["status"])
        self.assertNotIn("user_key", r)


def build_clue_api_client_from_default_test_config():
    cfg = ConfigParser.RawConfigParser()
    cfg.read(config_filepath)
    cao = clue_api_client.ClueApiClient(base_url=cfg.get(config_section, "clue_api_url"),
                                  user_key=cfg.get(config_section, "clue_api_user_key"))
    return cao


def add_entry_if_not_already_present(my_clue_api_orm, resource_name, where_query, default_data):
    check_result = my_clue_api_orm.run_count_query(resource_name, where_query)
    if check_result["count"] == 0:
        lookup_result = my_clue_api_orm.run_post(resource_name, default_data)
    else:
        lookup_result = my_clue_api_orm.run_filter_query(resource_name, {"where":where_query})[0]

    return lookup_result


if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    cao = build_clue_api_client_from_default_test_config()

    unittest.main()
