
from setuptools import setup

setup (name="dnm_cohorts",
    description='Package for obtaining cohorts used for de novo mutation analysis',
    version="1.0.0",
    author="Jeremy McRae",
    author_email="jmcrae@illumina.com",
    url='https://git.illumina.com/jmcrae/dnm_cohorts',
    packages=["dnm_cohorts", "dnm_cohorts.cohorts", "dnm_cohorts.de_novos"],
    install_requires=['pandas',
        'xlrd',
        'pdfminer.six',
        'requests',
        'hgvs',
    ],
    package_data={"dnm_cohorts": ['data/de_novos.txt.gz', 'data/cohort.txt.gz']},
    entry_points={'console_scripts': ['dnm_cohorts = dnm_cohorts.__main__:main']},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ])
 
