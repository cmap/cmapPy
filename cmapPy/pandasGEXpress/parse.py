"""
Generic parse method to parse either a .gct or a .gctx. 

Takes in a file path corresponding to either a .gct or .gctx, 
    and parses to a GCToo instance accordingly.

Note: Supports GCT1.2, GCT1.3, and GCTX1.0 files. 
"""
import logging
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.pandasGEXpress.parse_gct as parse_gct
import cmapPy.pandasGEXpress.parse_gctx as parse_gctx

__author__ = "Oana Enache"
__email__ = "oana@broadinstitute.org"

# instantiate logger
logger = logging.getLogger(setup_logger.LOGGER_NAME)


def parse(file_path, convert_neg_666=True, rid=None, cid=None, ridx=None, cidx=None,
          row_meta_only=False, col_meta_only=False, make_multiindex=False):
    """
    Identifies whether file_path corresponds to a .gct or .gctx file and calls the
    correct corresponding parse method.

    Input:
        Mandatory:
        - gct(x)_file_path (str): full path to gct(x) file you want to parse.

        Optional:
        - convert_neg_666 (bool): whether to convert -666 values to numpy.nan or not
            (see Note below for more details on this). Default = False.
        - rid (list of strings): list of row ids to specifically keep from gctx. Default=None.
        - cid (list of strings): list of col ids to specifically keep from gctx. Default=None.
        - ridx (list of integers): only read the rows corresponding to this
            list of integer ids. Default=None.
        - cidx (list of integers): only read the columns corresponding to this
            list of integer ids. Default=None.
        - row_meta_only (bool): Whether to load data + metadata (if False), or just row metadata (if True)
            as pandas DataFrame
        - col_meta_only (bool): Whether to load data + metadata (if False), or just col metadata (if True)
            as pandas DataFrame
        - make_multiindex (bool): whether to create a multi-index df combining
            the 3 component dfs

    Output:
        - out (GCToo object or pandas df): if row_meta_only or col_meta_only, then
            out is a metadata df; otherwise, it's a GCToo instance containing
            content of parsed gct(x) file

    Note: why does convert_neg_666 exist?
        - In CMap--for somewhat obscure historical reasons--we use "-666" as our null value
        for metadata. However (so that users can take full advantage of pandas' methods,
        including those for filtering nan's etc) we provide the option of converting these
        into numpy.NaN values, the pandas default.
    """
    if file_path.endswith(".gct"):
        out = parse_gct.parse(file_path, convert_neg_666=convert_neg_666,
                              rid=rid, cid=cid, ridx=ridx, cidx=cidx,
                              row_meta_only=row_meta_only, col_meta_only=col_meta_only,
                              make_multiindex=make_multiindex)

    elif file_path.endswith(".gctx"):
        out = parse_gctx.parse(file_path, convert_neg_666=convert_neg_666,
                              rid=rid, cid=cid, ridx=ridx, cidx=cidx,
                              row_meta_only=row_meta_only, col_meta_only=col_meta_only,
                              make_multiindex=make_multiindex)

    else:
        err_msg = "File to parse must be .gct or .gctx!"
        logger.error(err_msg)
        raise Exception(err_msg)

    return out

