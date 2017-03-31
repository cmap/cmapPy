# pandasGEXpress library 

This is a package of Python scripts that enable reading, writing, and basic modifications (slicing, concatenation) of .gct and .gctx files.

pandasGEXpress will eventually be a package available on Bioconda, but for now it is a component of the l1ktools repository. Briefly, l1ktools provides basic parse/slice/writing functionality in Matlab, Python, and R for those interacting with .gct and .gctx files. 

## Maintainer

Oana Enache 
oana@broadinstitute.org  
October 2016

## What is GCToo? 

GCToo is a class representing the contents of .gct or .gctx files. For instance, a GCT file is represented as illustrated in the blue figure at left; parsing in a file creates a GCToo instance with the attributes delimited at right. 

![GCT_to_GCToo](https://github.com/cmap/l1ktools/blob/master/python/broadinstitute_cmap/io/GCToo/simple_GCT_to_GCToo_figure.png)

## Setting up your environment

### To set up your environment the first time:

*NOTE* We intend to package and distribute this on Bioconda soon; when this occurs, installation instructions will change (hopefully to become even easier!). 

#### (if applicable) Install miniconda

1. Install miniconda (if you don't have it already!). Download/follow installation instructions from http://conda.pydata.org/miniconda.html. Unless you have personal preferences/reasons for doing so, we recommend installing Miniconda over Anaconda (it's more lightweight).

2. Type `conda info` to verify that conda has been installed on your system. You should see some information about the "Current conda install." If you don't, then conda has not been installed properly.

#### Clone l1ktools to a local directory

1. Clone the l1ktools directory ([l1ktools](https://github.com/cmap/l1ktools "l1ktools")) onto your computer. For example, I might clone it to `/Users/my_name/code/l1ktools`.

2. We will now a run a script to make our environment aware of files that we need. (You may need to checkout a different branch first; try `git checkout develop`.) Move to the `python` directory and run another setup script by typing the following:
    
      ```
      cd /Users/my_name/code/l1ktools/python/
      python setup.py develop
      ```

#### Setup the pandasGEXpress conda environment for the first time 

More details can be found here:http://conda.pydata.org/docs/using/envs.html#create-an-environment

1. To create the pandasGEXpress environment (with appropriate versions of packages), type the following:

      ```
      conda create --name pandasGEXpress python=2.7.11 numpy=1.11.2 pandas=0.18 h5py=2.6.0 
      ```

2. Activate the new environment (pandasGEXpress)
    
    On Windows:
     ```
     activate pandasGEXpress
     ```
    
    On Linux, OS X: 
     ```
     source activate pandasGEXpress
     ```
    
3. Check that the environment was installed correctly by typing: 
     ```
     conda list
     ```
    The packages listed should be the same as those in conda_environment.yml. 

### To set up your environment after the first time:

  1. Activate your conda environment by typing:
       
    On Windows:
     ```
     activate pandasGEXpress
     ```
    
    On Linux, OS X: 
     ```
     source activate pandasGEXpress
     ```
  2. It's easiest to run your code from the `pandasGEXpress` directory, so move there. For instance, if we wanted to run a test we would do the following:  
    
      ```
      cd /Users/my_name/code/l1ktools/python/broadinstitute_cmap/io/pandasGEXpress
      python test_parse_gctx.py
       ```

## Adding packages to your environment
For instance, if you'd like to add matplotlib, plotly, seaborn, etc. Activate your GCToo conda environment, then type the following:
```
conda install --name pandasGEXpress matplotlib
```
...and follow instructions. 

More details at: http://conda.pydata.org/docs/using/pkgs.html#install-a-package

## Example workflow 

Several examples of common tasks and the syntax you'd use to do them can be found [here](https://github.com/cmap/l1ktools/blob/master/python/broadinstitute_cmap/io/pandasGEXpress/Using%20pandasGEXpress%20-%20a%20tutorial%20of%20common%20tasks.ipynb)
