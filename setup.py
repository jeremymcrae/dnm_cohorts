
from setuptools import setup

setup (
    package_data={"dnm_cohorts": ['data/de_novos.txt.gz',
                                  'data/de_novos.grch37.txt.gz',
                                  'data/de_novos.grch38.txt.gz',
                                  'data/cohort.txt.gz']},
    )
