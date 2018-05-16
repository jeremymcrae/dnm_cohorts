
import pandas

from dnm_cohorts.person import Person
from dnm_cohorts.mock_probands import add_mock_probands

url = 'https://www.nature.com/nature/journal/v542/n7642/extref/nature21062-s2.xlsx'

def open_mcrae_nature_cohort():
    """ get proband details for McRae et al., Nature 2017
    
    McRae et al Nature 2017 542:433-438
    doi: 10.1038/nature21062
    Supplementary table S1.
    """
    data = pandas.read_excel(url, sheet_name='Supplementary Table 1')
    data['Individual ID'] += '|DDD'
    
    phenotype = 'intellectual_disability'
    
    persons = set()
    for i, row in data.iterrows():
        person = Person(row['Individual ID'], row.Sex, phenotype)
        persons.add(person)
    
    persons = add_mock_probands(persons, 4293, 'ddd', 'DDD', phenotype)
    
    return persons
