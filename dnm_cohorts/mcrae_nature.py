
import pandas

from dnm_cohorts.person import Person
from dnm_cohorts.mock_probands import add_mock_probands

url = 'https://media.nature.com/original/nature-assets/nature/journal/v542/n7642/extref/nature21062-s2.xlsx'

def open_mcrae_nature_cohort():
    data = pandas.read_excel(url, sheet_name='Supplementary Table 1')
    
    study = 'mcrae_nature_2017'
    phenotype = 'intellectual_disability'
    
    persons = set()
    for i, row in data.iterrows():
        person = Person({'person_id': row['Individual ID'], 'sex': row.Sex,
            'phenotype': phenotype, 'study': study})
        persons.add(person)
    
    persons = add_mock_probands(persons, 4293, 'ddd', study, phenotype)
    
    return list(persons)
