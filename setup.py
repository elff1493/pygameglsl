from setuptools import setup

setup(
   name='pyglsl',
   version='1.0',
   description='A useful module',
   author='el',
   #author_email=' ',
   packages=['glsl'],  #same as name
   py_modules=["shader", 'decomp'],
   install_requires=['pyopengl', 'pygame'],  # external packages as dependencies
   #scripts=[
    #        'shader',
     #       'decomp',
     #      ]
)