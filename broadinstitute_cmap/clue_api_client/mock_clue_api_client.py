import logging
import setup_logger
import clue_api_client

__authors__ = "David L. Lahr"
__email__ = "dlahr@broadinstitute.org"


logger = logging.getLogger(setup_logger.LOGGER_NAME)


class MockClueApiClient(clue_api_client.ClueApiClient):
    def __init__(self, base_url=None, user_key=None, default_return_values=None, filter_query_result=None,
        count_query_result=None, post_result=None, delete_result=None, put_result=None):

        super(MockClueApiClient, self).__init__(base_url=base_url, user_key=user_key)

        self.default_return_values = default_return_values if default_return_values else []

        self.filter_query_result = filter_query_result if filter_query_result else self.default_return_values

        self.count_query_result = count_query_result if count_query_result else self.default_return_values

        self.post_result = post_result if post_result else self.default_return_values

        self.delete_result = delete_result if delete_result else self.default_return_values

        self.put_result = put_result if put_result else self.default_return_values

    def run_filter_query(self, resource_name, filter_clause):
        return self.filter_query_result

    def run_count_query(self, resource_name, where_clause):
        return self.count_query_result

    def run_post(self, resource_name, data):
        return self.post_result

    def run_delete(self, resource_name, id):
        return self.delete_result

    def run_put(self, resource_name, id, data):
        return self.put_result
