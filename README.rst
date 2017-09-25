|install with bioconda|

.. |install with bioconda| image:: https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat-square
   :target: http://bioconda.github.io/recipes/cmappy/README.html
   
.. image:: https://badge.fury.io/py/cmapPy.svg
    :target: https://badge.fury.io/py/cmapPy
    
.. image:: https://readthedocs.org/projects/cmappy/badge/?version=latest
    :target: http://cmappy.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

**cmapPy:** Tools for interacting with .gctx and .gct files, and other Connectivity Map resources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**Connectivity Map, Broad Institute of MIT and Harvard**

`<http://cmappy.readthedocs.io/en/latest/>`_

For more information on the file formats and available resources, please see `clue.io/code <https://clue.io/code>`_.

Maintainer
==========

oana@broadinstitute.org

For questions/problems, please add an issue (that includes code/files that reproduce your problem) to the repository. 

Requirements
======================

As of April 11th, 2017, cmapPy has the following dependencies:

- **Python 2.7** (specifically, we use 2.7.11)
- h5py==2.6.0
- numpy==1.11.2
- pandas==0.18
- requests==2.13.0

Note that more recent versions of these packages should also work (except for Python3), should you choose to use them; however, we cannot guarantee package behavior for more recent packages. For contributors (see "Contributing" for further details), we request that you develop and submit any pull requests using the above environment. 

Installation and setup
======================

We recommend the use of cmapPy with a virtual environment (here we demonstrate how to use it with conda). 

**Option 1 (recommended): Setup pandasGEXpress in a new conda environment**

* (Mac and Windows; If you haven't already) install ``miniconda``
	* Download/follow instructions provided `here <https://conda.io/miniconda.html>`_. Unless you have personal preferences/reasons to do so, we recommend installing Miniconda over Anaconda because it's more lightweight.
	* On the command line, type ``conda info`` to verify that conda has been properly instaled on your system. You should see some information about the "current conda install"; if not, your installation didn't work. 
* (Mac only) Set up your conda channels: 
	``conda config --add channels defaults``
	
	``conda config --add channels conda-forge``
	
	``conda config --add channels bioconda``

* (Mac) Create & activate your cmapPy environment:
	``conda create --name my_cmapPy_env python=2.7.11 numpy=1.11.2 pandas=0.18 h5py=2.6.0 requests==2.13.0 cmappy``
	
	``source activate my_cmapPy_env``
	
* (Windows) Create & activate your cmapPy environment: 
	``conda create --name my_cmapPy_env python=2.7.11 numpy=1.11.2 pandas=0.18 h5py=2.6.0 requests==2.13.0``
	
	``pip install cmapPy``
	
	``source activate my_cmapPy_environment``

...and then cmapPy (including command line tools) should be available for use. 

To update cmapPy in your conda environment (from activate environment): ``conda update cmappy``

**Option 2: Install cmapPy from PyPI**

* ``pip install cmapPy``
* Note: For use of other virtualenvs, we include a requirements.txt file in the cmapPy package that you can use to install the proper versions of depencies.


Subpackages included
====================

* **pandasGEXpress**: Parsers, writers, and utility methods for .gctx and .gct files. Integrated with `pandas <http://pandas.pydata.org/>`_, enabling easy access to popular and powerful Python data science tools for analysis pipelines. 

* **cmap_api_client**: A Python API client for accessing and retrieving information from the `Connectivity Map API <https://clue.io/api>`_

* **set_io**: Parsers and writers for .grp and .gmt files.

***************
1) pandasGEXpress
***************

Contents Overview
"""""""""""""""""
pandasGEXpress represents .gctx and .gct files as instances of a GCToo object; in essence, this is a class that contains and maintains requirements between separate pandas DataFrames of the files' expression data, row metadata, and column metadata and some file attributes (source, version). More details on `clue.io/code <https://clue.io/code>`_. **Note that we currently only support GCTX version 1.0 and GCT versions 1.2 and 1.3**. 
 
* ``GCToo.py``: main class for storing contents of .gctx, .gct files.
* ``concat_gctoo.py``: Concatenate (horizontally or vertically) two or more GCToo instances in a  Python session or two {.gct, .gctx} files from the command line. 
* ``parse.py``: Parse in .gct, .gctx files to a new GCToo instance
* ``random_slice.py``: Slices a random subset of a GCToo file to a specified size. 
* ``slice_gct.py``: Slice a GCToo instance by including/excluding a list of row ids, column ids, row indexes, column indexes, or a combination thereof.
* ``write_gct.py``: Write a .gct file from a GCToo instance. 
* ``write_gctx.py``: Write a .gctx file from a GCToo instance.
A suite of unit tests is also included in the ``/tests`` directory. Sample files for testing can be found in ``/tests/functional_tests``.

**Command line tools**

* ``gct2gctx``: Command line tool to convert a .gct file to .gctx.
* ``gct2gctx``: Command line tool to convert a .gct file to a .gctx
* ``concat_gctoo``: Command line tool to stack .gct/x objects either vertically or horizontally 
* ``slice_gct``: Slice a .gct/x file to a specified set of rids and/or cids 

Tutorials and example use
"""""""""""""""""""""""""
* Tutorial: Accessing and processing GEO data `can be found here.`_

.. _can be found here.: https://github.com/cmap/cmapPy/blob/master/tutorials/cmapPy_pandasGEXpress_tutorial.ipynb

***************
2) cmap_api_client
***************

clue_api_client is a simple class that can be used to query the CLUE API. 

Contents Overview
"""""""""""""""""
* ``cell_queries.py``: Methods for cell line-related queries.
* ``clue_api_client.py``: Main class representing a client, for running queries against the CLUE API. 
* ``gene_queries.py``: Methods for gene-related queries. 
* ``macchiato_queries.py``: Methods for brew_prefix related queries. 
* ``mock_clue_api_client.py``: Mock API for testing.
* ``pert_queries.py``: Methods for perturbagen-related queries.

Tutorials and example use
"""""""""""""""""""""""""
Coming soon!

***************
3) set_io
***************

set_io contains simple scripts for parsing two other common file types used by the Connectivity Map: `GRP and GMT files. <https://clue.io/connectopedia/grp_gmt_gmx_format>`_ The GRP file is used for storing a single set of things (e.g. a single gene set), while the GMT file is used for storing multiple sets of things (e.g. several gene sets).

Contents Overview
"""""""""""""""""
* ``grp.py``: Read and write .grp files to a list.
* ``gmt.py``: Read and write .gmt files to a list of dictionaries.

Contributing
====================

We welcome contributors! For your pull requests, please include the following:

* Sample code/file that reproducibly causes the bug/issue
* Documented code providing fix
* Unit tests evaluating added/modified methods. 


Citation
====================

If you use cmapPy for your research, please cite us. Citation forthcoming; email oana@broadinstitute.org if you need one sooner.  
