
import pandas

from dnm_cohorts.person import Person

url = 'https://www.nature.com/nature/journal/v485/n7397/extref/nature10989-s2.xls'

def open_oroak_cohort():
    data = pandas.read_excel(url, sheet_name='Supplementary Table 1',
        skipfooter=1)
    
    status = 'autism'
    persons = set()
    for i, row in data.iterrows():
        person_type = row.child.split('.')[1]
        if person_type.startswith('s'):
            continue
        
        person = Person(row.child + '|asd_cohorts', row.sex, status)
        persons.add(person)
    
    return persons
