
from pkg_resources import resource_filename

import pandas

DE_NOVO_PATH = resource_filename(__name__, "data/de_novos.txt.gz")
COHORT_PATH = resource_filename(__name__, "data/cohort.txt.gz")

def open_de_novos():
    return pandas.read_table(DE_NOVO_PATH)

def open_cohort():
    return pandas.read_table(COHORT_PATH)

de_novos = open_de_novos()
cohort = open_cohort()
