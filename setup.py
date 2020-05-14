from setuptools import setup, find_packages, Extension
from distutils.command.build_ext import build_ext as _build_ext

with open("README.md", "r") as fh:
    long_description = fh.read()
class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())

setup(
    name="opticam",
    version="0.1",
    ext_modules=[
                 Extension('analysis', [r'C:\Users\RMabrouk\Documents\Opticam\opticam\analysis.c']),
                 Extension('segmentation', [r'C:\Users\RMabrouk\Documents\Opticam\opticam\segmentation.c']),
                 Extension('entrygate', [r'C:\Users\RMabrouk\Documents\Opticam\opticam\entrygate.c']),
                 Extension('logwriter', [r'C:\Users\RMabrouk\Documents\Opticam\opticam\logwriter.c']),
                 Extension('decision', [r'C:\Users\RMabrouk\Documents\Opticam\opticam\decision.c'])
                 ],
    author='Rostom Mabrouk',
    author_email='Rostom.mabrouk@synmedrx.com',
    description='Analyse Pill for Synergy Medical',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Rostom44/opticam",

    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    setup_requires=['numpy'],
    cmdclass={'build_ext': build_ext},
    #install_requires=['mahotas',
     #       'numpy',
      #      'scipy',
       #     'json',
        #    'collections',
         #   'opencv',
          #  'os',
           # 'skimage',
            #'math',
            #'pickle',
            #'operator',
            #'termcolor',
            #'colorama']
)

