
from setuptools import setup

setup (name="dnm_cohorts",
    description='Package for obtaining cohorts used for de novo mutation analysis',
    version="1.0.0",
    author="Jeremy McRae",
    author_email="jmcrae@illumina.com",
    url='https://git.illumina.com/jmcrae/dnm_cohorts',
    packages=["dnm_cohorts"],
    install_requires=['pandas',
        'pdfminer.six',
        'requests',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ])
 
