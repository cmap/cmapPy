.. _install:

Installation
============

We  highly recommend the using a prebuilt distribution of cmapPy along with a virtual environment (here we demonstrate how to use it with conda).

**Option 1 (recommended): Setup pandasGEXpress in a new conda environment**

* (All operating systems; If you haven't already) install ``miniconda``
	* Download/follow instructions provided `here <https://conda.io/miniconda.html>`_. Unless you have personal preferences/reasons to do so, we recommend installing Miniconda over Anaconda because it's more lightweight.
	* On the command line, type ``conda info`` to verify that conda has been properly instaled on your system. You should see some information about the "current conda install"; if not, your installation didn't work.

* (Linux and Mac) Create & activate your cmapPy environment:

	Note. We currently use Python 2.7.11 for our production code (hence its specification); however, other versions of Python 2 should be stable as well. We do not currently support Python 3. 

	**Step 1** 

	Python 2: ``conda create --name my_cmapPy_env -c bioconda python=2.7.11 numpy=1.11.2 pandas=0.20.3 h5py=2.7.0 requests==2.13.0 cmappy``

	* ``-c bionconda`` tells conda that it should look for packages in the bioconda channel (that's where cmapPy lives)


	**Step 2**

	``source activate my_cmapPy_env``

* (Windows) Create & activate your cmapPy environment:

	**Step 1**

	Python 2: ``conda create --name my_cmapPy_env python=2.7.11 numpy=1.11.2 pandas=0.20.3 h5py=2.7.0 requests==2.13.0``

	**Step 2**

	``pip install cmapPy``

	``source activate my_cmapPy_env``

...and then cmapPy (including command line tools) should be available for use.

To update cmapPy in your conda environment (from activate environment): ``conda update cmappy``

**Option 2: Install cmapPy from PyPI**

* ``pip install cmapPy``
* Note: For use of other virtualenvs, we include a requirements.txt file in the cmapPy package that you can use to install the proper versions of depencies.

**Option 3: Install as a development environment**

A development environment will allow you to use the cmapPy code as it is in a clone of the repository, allowing you to try out changes and modifications you may wish to make.

Follow the instructions for Option 1 or Option 2 above but change the name of the environment to e.g. ``my_cmapPy_dev_env`` and do not include ``cmappy`` in the list of packages to install (or do not install it with pip), then activate this environment, i.e.:
	
	Python 2.7: ``conda create --name my_cmapPy_dev_env python=2.7.11 numpy=1.11.2 pandas=0.20.3 h5py=2.7.0 requests==2.13.0``
	
	``source activate my_cmapPy_dev_env``

Clone the cmapPy github repository, cd into the repo's top-level directory, and run:

	``$ python setup.py develop``

To test your setup, change into a directory outside the repo, run the python interpreter and try:
	``cd <ELSEWHERE>``

	``$ python``

	``>> import cmapPy.pandasGEXpress.parse_gct as pg``
