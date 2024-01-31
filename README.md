# PyNARS

#### Description
Python implementation of NARS (Non-Axiomatic-Reasoning-System)

Reference:
 - OpenNARS 3.0.4, 
 - The Design Report of OpenNARS 3.1.0


#### Environments

 - Python version: 3.7.10. 
     - Only tested under this version, however, Python 3.7 and higher versions maybe acceptable.
 - OS: Windows 10. 
     - Only tested under this OS, however, other OSs might be ok.
 - Packages Requirements: see `requirements.txt`.
     - It is noted that the version of the python package `tqdm` should be no higher than 3.1.4, otherwise the color display would be abnormal. This is because of a bug of `tqdm`, which leads to conflicts between `sty` and `tqdm` and cause unexpected color display of `sty`. However, this constraints is not necessary, i.e., higher version of `tqdm` is ok if you don't mind abnormal display occuring. The abnormal case only occurs if you first run PyNARS when SparseLUT (Sparse Look-Up Table) is built.

#### Installation


    pip install pynars


#### Instructions

1.  Copy the file `pynars/config.json` to your workspace-directory. *(Optional)*
2.  In the workspace-directory, run cmd `python -m pynars.Console`. To execute an `*.nal` file, run cmd `python -m pynars.Console <your-file-name.nal>`
3.  Input Narsese in the console, input an positive integer to run a number of cycles, or input a comment which is a string with `'` as the beginning, e.g. `' your comment`.
4.  Press `ctrl`+`C` to exit.

To develop PyNARS, clone this project by 
```
git clone https://github.com/bowen-xu/PyNARS.git
```
and then update submodule(s) by
```
git submodule update --init --recursive
```


#### Contribution

1.  Fork the repository
2.  Create Feat_xxx branch
3.  Commit your code
4.  Create Pull Request


**Note:** This document will be imporved in the future.