.. _install:

Installation
============

We  highly recommend the using a prebuilt distribution of cmapPy along with a virtual environment (here we demonstrate how to use it with conda). 

**Option 1 (recommended): Setup pandasGEXpress in a new conda environment**

* (If you haven't already) install ``miniconda``
	* Download/follow instructions provided `here <https://conda.io/miniconda.html>`_. Unless you have personal preferences/reasons to do so, we recommend installing Miniconda over Anaconda because it's more lightweight.
	* On the command line, type ``conda info`` to verify that conda has been properly instaled on your system. You should see some information about the "current conda install"; if not, your installation didn't work. 
* Create your cmapPy environment: ``conda create --name my_cmapPy_env python=2.7.11 numpy=1.11.2 pandas=0.18 h5py=2.6.0 requests==2.13.0``
* Activate your cmapPy environment: ``source activate my_cmapPy_env``
* **In your activated conda environment**, pip install cmapPy: ``pip install cmapPy``

**Option 2: Install cmapPy from PyPI**

* ``pip install cmapPy``
* Note: For use of other virtualenvs, we include a requirements.txt file in the cmapPy package that you can use to install the proper versions of depencies.

