
import os
import random

import pandas

from dnm_cohorts.hashdict import Hashdict
from dnm_cohorts.mock_probands import add_mock_probands

url = 'https://media.nature.com/original/nature-assets/nature/journal/v515/n7526/extref/nature13772-s4.xlsx'
alternate = 'http://www.cell.com/cms/attachment/2118908541/2086568191/mmc6.xlsx'

def open_additional():
    data = pandas.read_excel(alternate, sheet_name='Exome')
    
    data = data[data.Study == 'ASC_DeRubeis']
    data['person_id'] = data['patientID']
    data['sex'] = data['Sex'].map({1: 'male', 2: 'female'})
    data['phenotype'] = data['Phenotype'].map({1: 'unaffected', 2: 'autism'})
    
    return data[['person_id', 'sex', 'phenotype']]

def open_de_rubeis_cohort():
    data = pandas.read_excel(url, sheet_name='De Novo', skip_footer=1)
    
    # clean up a couple of columns
    data['person_id'] = data.Child_ID
    data['sex'] = data.Child_Sex.map({1: 'male', 2: 'female'})
    data['phenotype'] = data['Child_AffectedStatus'].map({1: 'unaffected', 2: 'autism'})
    data = data[['person_id', 'sex', 'phenotype']]
    
    additional = open_additional()
    data = data.append(additional, ignore_index=True)
    
    study = 'de_rubeis_nature_2014'
    
    persons = set()
    for i, row in data.iterrows():
        person = Hashdict({'person_id': row.person_id, 'sex': row.sex,
            'phenotype': row.phenotype, 'study': study})
        persons.add(person)
    
    persons = add_mock_probands(persons, 1445, 'asd', study, 'autism')
    
    return list(persons)

a = open_de_rubeis_cohort()
