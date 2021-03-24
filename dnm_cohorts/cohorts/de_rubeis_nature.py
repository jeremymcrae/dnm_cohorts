
import os

import pandas

from dnm_cohorts.person import Person
from dnm_cohorts.mock_probands import add_mock_probands

url = 'https://static-content.springer.com/esm/art%3A10.1038%2Fnature13772/MediaObjects/41586_2014_BFnature13772_MOESM41_ESM.xlsx'
alternate = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4624267/bin/NIHMS723829-supplement-7.xlsx'

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
    Supplementary table S5 from Sanders et al. (2015) Neuron 87:1215-1233.
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
    study = ['10.1038/nature13772']
    
    persons = set()
    for i, row in data.iterrows():
        person = Person(row.person_id, row.sex, row.phenotype, study)
        persons.add(person)
    
    persons = add_mock_probands(persons, 1445, 'asd', 'asd_cohorts', ['HP:0000717'], study)
    
    return persons
