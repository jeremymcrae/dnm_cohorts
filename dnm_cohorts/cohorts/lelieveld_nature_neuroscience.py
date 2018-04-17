
import random
random.seed(1)

import pandas

from dnm_cohorts.person import Person

url = 'https://media.nature.com/original/nature-assets/neuro/journal/v19/n9/extref/nn.4352-S3.xlsx'

def open_lelieveld_cohort():
    data = pandas.read_excel(url, sheet_name='Supplementary Table 2')
    
    study = 'lelieveld_nature_neuroscience_2016'
    phenotype = 'intellectual_disability'
    
    ids = list(range(1, max(data['Patient key']) + 1))
    male_fraction = 461 / (461 + 359)
    
    persons = set()
    for person_id in ids:
        sex = 'male' if random.random() < male_fraction else 'female'
        person = Person(person_id, sex, phenotype, study)
        persons.add(person)
    
    return persons
