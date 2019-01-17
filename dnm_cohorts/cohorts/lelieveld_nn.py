
import random

import pandas

from dnm_cohorts.person import Person

url = 'https://www.nature.com/neuro/journal/v19/n9/extref/nn.4352-S3.xlsx'

def open_lelieveld_cohort():
    """ get proband details for Lelieveld et al., 2016
    
    Lelieveld et al. (2016) Nature Neuroscience 19:1194-1196
    doi: 10.1038/nn.4352
    Supplementary table S2.
    """
    random.seed(1)
    data = pandas.read_excel(url, sheet_name='Supplementary Table 2')
    
    phenotype = 'intellectual_disability'
    
    ids = list(range(1, max(data['Patient key']) + 1))
    ids = [ str(x) + '|lelieveld' for x in ids ]
    male_fraction = 461 / (461 + 359)
    
    persons = set()
    for person_id in ids:
        sex = 'male' if random.random() < male_fraction else 'female'
        person = Person(person_id, sex, phenotype)
        persons.add(person)
    
    return persons
