
import os

import pandas

from dnm_cohorts.person import Person

url = 'http://www.cell.com/cms/attachment/2118908541/2086568189/mmc2.xlsx'

def open_sanders_neuron_cohort():
    data = pandas.read_excel(url, sheet_name='Sheet1')
    
    
    sexes = {'F': 'female', 'female': 'female', 'M': 'male', 'male': 'male',
        'U': 'unknown'}
    study = 'sanders_neuron_2015'
    
    persons = set()
    for i, row in data.iterrows():
        if row.Father == '.' or row.Mother == '.':
            continue
        
        if row.Cohort == 'SSC_Removed':
            continue
        
        for sample in ['Proband', 'Sibling']:
            if row[sample] == '.':
                continue
            
            sex = sexes[row['{}Sex'.format(sample)]]
            phenotype = 'unaffected' if sample == 'Sibling' else 'autism'
            
            person = Person({'person_id': row[sample], 'sex': sex,
                'phenotype': phenotype, 'study': study})
            persons.add(person)
    
    return list(persons)
