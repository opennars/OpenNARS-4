# python setup.py build_ext --inplace
from setuptools import setup
from Cython.Build import cythonize
from mypy import stubgen

options = stubgen.parse_options(['sparse_lut.py', 'branch_list.py', '-o', '.'])
stubgen.generate_stubs(options)

setup(
    name='sparse_lut',
    version='1.0.0',
    ext_modules=cythonize(
        ['./sparse_lut.py', 
        './branch_list.py'],
        annotate=True),                 # enables generation of the html annotation file
)