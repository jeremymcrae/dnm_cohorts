
import pandas

from dnm_cohorts.person import Person

url = 'https://www.nature.com/nature/journal/v485/n7397/extref/nature10989-s2.xls'

def open_oroak_cohort():
    """ get proband data from the O'Roak et al autism exome study
    
    O'Roak et al. (2012) Nature 485:246-250
    doi: 10.1038/nature10989
    Supplementary table 1
    """
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
