
import random

import pandas

from dnm_cohorts.person import Person
from dnm_cohorts.mock_probands import add_mock_probands

url = 'https://www.biorxiv.org/content/biorxiv/early/2019/10/16/797787/DC2/embed/media-2.txt'

def subcohort(rows, counts, prefix, suffix):
    '''
    '''
    phenotype = ['HP:0001249']
    total = sum(counts.values())
    male_fraction = counts['male'] / total
    
    persons = set()
    for i, row in rows.iterrows():
        sex = 'male' if random.random() < male_fraction else 'female'
        person = Person(row['person_id'], sex, phenotype)
        persons.add(person)
    
    # account for individuals without exomic de novo mutations
    return add_mock_probands(persons, total, prefix, suffix, phenotype)

def kaplanis_biorxiv_cohort():
    """ get proband details for Kaplanis et al BioRxiv 2019
    
    Kaplanis et al BioRxiv 2019
    doi: 10.1101/797787
    Supplementary Table S1.
    """
    random.seed(1)
    data = pandas.read_table(url)
    
    # define male and female numbers for each of the subcohorts (DDD, geneDx and
    # RUMC). These use the subcohort totals from the supplementary information.
    # For DDD and geneDx male and female counts were estimated from length of
    # male bars in supp fig 2A. The total cohort had 8 duplicates removed, so
    # I dropped 2 from DDD, 3 from geneDx, and 2 from RUMC.
    counts = {'DDD': {'male': 5659, 'female': 4197},
        'GDX': {'male': 10387, 'female': 8399},
        'RUMC': {'male': 1377, 'female': 1039}}
    
    data['person_id'] = data['id'] + '|' + data['study']
    phenotype = ['HP:0001249']
    
    persons = set()
    for study in counts:
        rows = data[data['study'] == study]
        persons |= subcohort(rows, counts[study], study.lower(), study)
    
    return persons
