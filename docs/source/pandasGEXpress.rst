.. _pandasGEXpress:

GCT, GCTx (pandasGEXpress)
==========================

pandasGEXpress package (integrated with Python's `pandas <http://pandas.pydata.org/>`_ package) allowing users to easily read, modify, and write .gct and .gctx files. Note that .gctx files are more performant than .gct, and we recommend their use. 


GCToo Class
-----------
.. autoclass:: cmapPy.pandasGEXpress.GCToo.GCToo

Parsing
-------

.. autofunction:: cmapPy.pandasGEXpress.parse.parse

Writing
-------

.. autofunction:: cmapPy.pandasGEXpress.write_gctx.write

.. autofunction:: cmapPy.pandasGEXpress.write_gct.write

Concatenating
-------------

.. automodule:: cmapPy.pandasGEXpress.concat
   :members:

Converting .gct <-> .gctx
-------------------------

.. automodule:: cmapPy.pandasGEXpress.gct2gctx
   :members:

.. automodule:: cmapPy.pandasGEXpress.gctx2gct
   :members:

Extracting from .grp files
--------------------------

.. automodule:: cmapPy.pandasGEXpress.plategrp
   :members:

Subsetting
-------

.. automodule:: cmapPy.pandasGEXpress.random_slice
   :members:

.. automodule:: cmapPy.pandasGEXpress.subset
   :members:




