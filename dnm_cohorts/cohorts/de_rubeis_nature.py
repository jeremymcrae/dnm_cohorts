
import os

import pandas

from dnm_cohorts.person import Person
from dnm_cohorts.mock_probands import add_mock_probands

url = 'https://www.nature.com/nature/journal/v515/n7526/extref/nature13772-s4.xlsx'
alternate = 'http://www.cell.com/cms/attachment/2118908541/2086568191/mmc6.xlsx'

def open_additional():
    data = pandas.read_excel(alternate, sheet_name='Exome')
    
    data = data[data.Study == 'ASC_DeRubeis']
    data['person_id'] = data['patientID']
    data['sex'] = data['Sex'].map({1: 'male', 2: 'female'})
    data['phenotype'] = data['Phenotype'].map({1: ['unaffected'], 2: ['HP:0000717']})
    
    return data[['person_id', 'sex', 'phenotype']]

def open_de_rubeis_cohort():
    """
    De Rubeis et al. (2013) Nature 515:209-215
    doi: 10.1038/nature13772
    Supplementary Table 3, with some additional proband details sourced from
    Supplementary table S4 from Sanders et al. (2015) Neuron 87:1215-1233.
    """
    data = pandas.read_excel(url, sheet_name='De Novo', skipfooter=1)
    
    # clean up a couple of columns
    data['person_id'] = data.Child_ID
    data['sex'] = data.Child_Sex.map({1: 'male', 2: 'female'})
    data['phenotype'] = data['Child_AffectedStatus'].map({1: ['unaffected'], 2: ['HP:0000717']})
    data = data[['person_id', 'sex', 'phenotype']]
    
    additional = open_additional()
    data = data.append(additional, ignore_index=True)
    data['person_id'] = data.person_id.astype(str)
    data['person_id'] += '|asd_cohorts'
    
    persons = set()
    for i, row in data.iterrows():
        person = Person(row.person_id, row.sex, row.phenotype)
        persons.add(person)
    
    persons = add_mock_probands(persons, 1445, 'asd', 'asd_cohorts', ['HP:0000717'])
    
    return persons
