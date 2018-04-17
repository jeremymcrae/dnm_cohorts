
import pandas

from dnm_cohorts.person import Person

url = 'https://media.nature.com/original/nature-assets/nature/journal/v485/n7397/extref/nature10989-s2.xls'

def open_oroak_cohort():
    data = pandas.read_excel(url, sheet_name='Supplementary Table 1')
    
    study = 'oroak_nature_2012'
    status = 'autism'
    persons = set()
    for i, row in data.iterrows():
        if row.child.endswith('s1'):
            continue
        
        person = Person(row.child, row.sex, status, study)
        persons.add(person)
    
    return persons
