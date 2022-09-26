
import logging
import random

import pandas

from dnm_cohorts.person import Person

url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5675000/bin/NIHMS906719-supplement-supp_datasets.xlsx'

def open_jin_nature_genetics_cohort():
    """ gets individual level data for Jin et al congenital heart disease
    
    Supplementary Table 1 from:
    Jin et al. Nature Genetics 49: 1593-1601, doi: 10.1038/ng.3970
    """
    logging.info('getting Jin et al Nature Genetics 2017 cohort')
    random.seed(1)
    data = pandas.read_excel(url, 'S1', skiprows=1)
    data['person_id'] = data['Blinded ID'].astype(str) + '|jin'
    
    # get male fraction in trios from cohort sex counts in supplemental table 2
    male_fraction = 1691 / (1691 + 1180)
    study = ['10.1038/ng.3970']
    
    persons = set()
    for i, row in data.iterrows():
        status = ['HP:0001627']
        sex = 'male' if random.random() < male_fraction else 'female'
        if row['NDD'] == 'Yes':
            status.append('HP:0001263')
        
        person = Person(row.person_id, sex, status, study)
        persons.add(person)
    
    return persons
