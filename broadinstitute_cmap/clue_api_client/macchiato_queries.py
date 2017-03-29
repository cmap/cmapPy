import logging
import setup_logger

__authors__ = "David L. Lahr"
__email__ = "dlahr@broadinstitute.org"


logger = logging.getLogger(setup_logger.LOGGER_NAME)

resource_name = "macchiato"

uploading_status = "UPLOADING"
uploaded_status = "UPLOADED"


def is_brew_prefix_in_api(my_clue_api_client, brew_prefix):
    my_where_clause = {"brew_prefix":brew_prefix}
    query_result = my_clue_api_client.run_count_query(resource_name, my_where_clause)
    logger.debug("query_result:  {}".format(query_result))
    return query_result["count"] == 1


def get_api_id(my_clue_api_client, brew_prefix):
    my_filter = {"where":{"brew_prefix":brew_prefix}, "fields":{"id":True}}
    id_result = my_clue_api_client.run_filter_query(resource_name, my_filter)
    logger.debug("id_result:  {}".format(id_result))
    return id_result[0]["id"]


def change_status(my_clue_api_client, api_id, new_status):
    r = my_clue_api_client.run_put(resource_name, api_id, {"status":new_status})
    return r


def create_brew_prefix_in_api(my_clue_api_client, brew_prefix, status=uploading_status):
    data = {"brew_prefix":brew_prefix, "status":uploading_status}
    r = my_clue_api_client.run_post(resource_name, data)
    return r
