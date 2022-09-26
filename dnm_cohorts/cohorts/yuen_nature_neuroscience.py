import logging
import random

import pandas

from dnm_cohorts.person import Person

url = 'https://static-content.springer.com/esm/art%3A10.1038%2Fnn.4524/MediaObjects/41593_2017_BFnn4524_MOESM53_ESM.xlsx'
dnms_url = 'https://static-content.springer.com/esm/art%3A10.1038%2Fnn.4524/MediaObjects/41593_2017_BFnn4524_MOESM49_ESM.xlsx'

def open_yuen_nature_genetics_cohort():
    """ gets individual level data for Yuen et al., 2017
    
    Supplementary Table 7 from:
    Yuen et al. (2017) Nature Neuroscience 20:602-611, 
    doi: 10.1038/nn.4524
    """
    logging.info(f'getting Yuen et al Nature Neuroscience 2017 cohort')
    random.seed(1)
    data = pandas.read_excel(url, 'Table S7', skiprows=1)
    data['person_id'] = data['SUBMITTED_ID'].astype(str) + '|asd_cohorts'
    
    phenotype = ['HP:0000717']
    study = ['10.1038/nn.4524']
    
    # restrict to samples with de novo muatations (1627 trios)
    dnms = pandas.read_excel(dnms_url, 'Table S3', skiprows=1)
    dnms['person_id'] = dnms['SAMPLE'].astype(str) + '|asd_cohorts'
    with_dnms = set(dnms['person_id'])
    data = data[data['person_id'].isin(with_dnms)]
    
    male_fraction = 2062 / (2062 + 558)
    
    persons = set()
    for row in data.itertuples():
        sex = 'male' if random.random() < male_fraction else 'female'
        person = Person(row.person_id, sex, phenotype, study)
        persons.add(person)
    
    return persons
