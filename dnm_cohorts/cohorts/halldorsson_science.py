
import random
import logging
import tempfile

import pandas

from dnm_cohorts.person import Person
from dnm_cohorts.download_file import download_file

url = 'https://www.science.org/doi/suppl/10.1126/science.aau1043/suppl_file/aau1043_datas5_revision1.tsv'

def open_halldorsson_science_cohort():
    """ get de novo variants for Halldorsson et al Science 2019
    
    Supplementary Data 5 (revised) from:
    Halldorsson et al. Science 343: eaau1043, doi: 10.1126/science.aau1043
    """
    random.seed(1)
    
    with tempfile.NamedTemporaryFile() as temp:
        # the url redirects, so use the requests package to open the URL
        download_file(url, temp.name)
        df = pandas.read_table(temp.name, comment='#')
    
    df['person_id'] = df['Proband_id'].astype(str)
    df['person_id'] += '|halldorsson'
    
    phenotype = ['unaffected']
    study = ['10.1038/nature24018']
    female_fraction = 0.5  # assumption from the fraction from their earlier Jonsson et al publication
    
    persons = set()
    for row in df.itertuples():
        sex = 'female' if random.random() < female_fraction else 'male'
        var = Person(row.person_id, sex, phenotype, study)
        persons.add(var)
    
    return persons
