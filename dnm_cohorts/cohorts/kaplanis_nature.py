
import random

import pandas

from dnm_cohorts.person import Person
from dnm_cohorts.mock_probands import add_mock_probands

url = 'https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-020-2832-5/MediaObjects/41586_2020_2832_MOESM3_ESM.txt'

def subcohort(rows, counts, prefix, suffix, study):
    '''
    '''
    phenotype = ['HP:0001249']
    total = sum(counts.values())
    male_fraction = counts['male'] / total
    
    persons = set()
    for i, row in rows.iterrows():
        sex = 'male' if random.random() < male_fraction else 'female'
        person = Person(row['person_id'], sex, phenotype, study)
        persons.add(person)
    
    # account for individuals without exomic de novo mutations
    return add_mock_probands(persons, total, prefix, suffix, phenotype, study)

def kaplanis_nature_cohort():
    """ get proband details for Kaplanis et al BioRxiv 2019
    
    Kaplanis et al Nature 2020
    doi: 10.1038/s41586-020-2832-5
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
    doi = ['10.1038/s41586-020-2832-5']
    
    persons = set()
    for study in counts:
        rows = data[data['study'] == study]
        persons |= subcohort(rows, counts[study], study.lower(), study, doi)
    
    return persons
