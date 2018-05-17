
import gzip
from pkg_resources import resource_filename

# import pandas
from dnm_cohorts.de_novo import DeNovo
from dnm_cohorts.person import Person

DE_NOVO_PATH = resource_filename(__name__, "data/de_novos.txt.gz")
COHORT_PATH = resource_filename(__name__, "data/cohort.txt.gz")

def open_de_novos():
    with gzip.open(DE_NOVO_PATH, 'rt') as handle:
        header = handle.readline()
        return [ DeNovo(*x.strip('\n').split('\t')) for x in handle ]

def open_cohort():
    with gzip.open(COHORT_PATH, 'rt') as handle:
        header = handle.readline()
        return [ Person(*x.strip('\n').split('\t')) for x in handle ]

de_novos = open_de_novos()
cohort = open_cohort()
