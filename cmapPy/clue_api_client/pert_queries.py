import logging
import setup_logger

__authors__ = "David L. Lahr"
__email__ = "dlahr@broadinstitute.org"


logger = logging.getLogger(setup_logger.LOGGER_NAME)

resource_name = "perts"


def retrieve_pert_id_pert_iname_map(pert_ids, my_clue_api_client):
    my_filter = {"where":{"pert_id":{"inq":pert_ids}}, "fields":{"pert_id":True, "pert_iname":True}}
    query_result = my_clue_api_client.run_filter_query(resource_name, my_filter)
    logger.debug("query_result:  {}".format(query_result))

    r = _build_map_from_clue_api_result(query_result, "pert_id", "pert_iname")
    return r


def retrieve_pert_id_pert_type_map(pert_ids, my_clue_api_client):
    my_filter = {"where":{"pert_id":{"inq":pert_ids}}, "fields":{"pert_id":True, "pert_type":True}}
    query_result = my_clue_api_client.run_filter_query(resource_name, my_filter)
    logger.debug("query_result:  {}".format(query_result))

    r = _build_map_from_clue_api_result(query_result, "pert_id", "pert_type")
    return r


def _build_map_from_clue_api_result(clue_api_result, key_field, value_field):
    r = {}
    for car in clue_api_result:
        key = car[key_field]
        value = car[value_field]
        r[key] = value

    return r

