
import logging

import pandas

from dnm_cohorts.person import Person

url = 'https://static-content.springer.com/esm/art%3A10.1038%2Fnature10989/MediaObjects/41586_2012_BFnature10989_MOESM11_ESM.xls'

def open_oroak_cohort():
    """ get proband data from the O'Roak et al autism exome study
    
    O'Roak et al. (2012) Nature 485:246-250
    doi: 10.1038/nature10989
    Supplementary table 1
    """
    logging.info('getting O\'Roak et al Nature 2012 cohort')
    data = pandas.read_excel(url, sheet_name='Supplementary Table 1',
        skipfooter=1, engine='xlrd')
    
    study = ['10.1038/nature10989']
    persons = set()
    for i, row in data.iterrows():
        status = ['HP:0000717']
        person_type = row.child.split('.')[1]
        # ignore the siblings, since they don't have any de novos recorded, so
        # don't contribute to the exome-sequence populations
        if person_type.startswith('s'):
            continue
        if row['non-verbal_IQ'] < 70:
            status.append('HP:0001249')
        
        person = Person(row.child + '|asd_cohorts', row.sex, status, study)
        persons.add(person)
    
    return persons
