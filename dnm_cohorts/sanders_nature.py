
import pandas

from dnm_cohorts.hashdict import Hashdict

url = 'https://media.nature.com/original/nature-assets/nature/journal/v485/n7397/extref/nature10945-s2.xls'

def open_sanders_nature_cohort():
    data = pandas.read_excel(url, sheet_name='Sheet1')
    
    study = 'sanders_nature_2012'
    
    persons = set()
    for i, row in data.iterrows():
        if row.Sample.endswith('fa') or row.Sample.endswith('mo'):
            # ignore parental samples
            continue
        
        status = 'autism'
        if row.Role == 'Unaffected_Sibling':
            status = 'unaffected'
        
        person = Hashdict({'person_id': row.Sample, 'sex': row.Gender.lower(),
            'phenotype': status, 'study': study})
        persons.add(person)
        
    return list(persons)
