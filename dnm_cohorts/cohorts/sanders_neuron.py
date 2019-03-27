
import os

import pandas

from dnm_cohorts.person import Person

url = 'http://www.cell.com/cms/attachment/2118908541/2086568189/mmc2.xlsx'

def open_sanders_neuron_cohort():
    """
    
    Supplementary Table 1 from:
    Sanders et al. (2015) Neuron 87:1215-1233
    doi: 10.1016/j.neuron.2015.09.016
    """
    data = pandas.read_excel(url, sheet_name='Sheet1')
    
    sexes = {'F': 'female', 'female': 'female', 'M': 'male', 'male': 'male',
        'U': 'unknown'}
    
    persons = set()
    for i, row in data.iterrows():
        if row.Father == '.' or row.Mother == '.':
            continue
        
        if row.Cohort == 'SSC_Removed':
            continue
        
        for sample in ['Proband', 'Sibling']:
            if row[sample] == '.':
                continue
            
            sex = sexes[row[f'{sample}Sex']]
            phenotype = 'unaffected' if sample == 'Sibling' else 'autism'
            
            person = Person(row[sample] + '|asd_cohorts', sex, phenotype)
            persons.add(person)
    
    return persons
