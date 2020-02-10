
import gzip
from pkg_resources import resource_filename

# import pandas
from dnm_cohorts.de_novo import DeNovo
from dnm_cohorts.person import Person

DE_NOVO_PATH = resource_filename(__name__, "data/de_novos.txt.gz")
DE_NOVO_PATH_b37 = resource_filename(__name__, "data/de_novos.grch37.txt.gz")
DE_NOVO_PATH_b38 = resource_filename(__name__, "data/de_novos.grch38.txt.gz")
COHORT_PATH = resource_filename(__name__, "data/cohort.txt.gz")

def open_de_novos(path=None):
    ''' opens de novos, loads file from repo by default
    
    Pass 'grch37' or 'grch38' to open variants lifted to that build.
    '''
    if not path:
        path = DE_NOVO_PATH
    elif isinstance(path, str) and path.lower() == 'grch37':
        path = DE_NOVO_PATH_b37
    elif isinstance(path, str) and path.lower() == 'grch38':
        path = DE_NOVO_PATH_b38
    
    with gzip.open(path, 'rt') as handle:
        header = handle.readline()
        return [ DeNovo(*x.strip('\n').split('\t')) for x in handle ]

def open_cohort(path=None):
    if not path:
        path = COHORT_PATH
    with gzip.open(path, 'rt') as handle:
        header = handle.readline()
        cohort = []
        for line in handle:
            person_id, sex, phenotypes, studies = line.strip('\n').split('\t')
            phenotypes = phenotypes.split(',')
            studies = studies.split(',')
            cohort.append(Person(person_id, sex, phenotypes, studies))
        return cohort

de_novos = open_de_novos()
cohort = open_cohort()
