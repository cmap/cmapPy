.. _set_io:

GRP, GMT (set_io) 
=================

set_io contains simple scripts for parsing two other common file types used by the Connectivity Map: GRP and GMT files. 
The GRP file is used for storing a single set of things (e.g. a single gene set), while the GMT file is used for storing multiple sets of things (e.g. several gene sets).

Further details on GRP and GMT files can be found `here
<https://clue.io/connectopedia/grp_gmt_gmx_format>`_.

Reading GRP files
-----------------

.. autofunction:: cmapPy.set_io.grp.read

Writing GRP files
-----------------

.. autofunction:: cmapPy.set_io.grp.write

Reading GMT files
-----------------

.. autofunction:: cmapPy.set_io.gmt.read

Verifying GMT integrity
-----------------------

.. autofunction:: cmapPy.set_io.gmt.verify_gmt_integrity

Writing GMT files
-----------------

.. autofunction:: cmapPy.set_io.gmt.write
