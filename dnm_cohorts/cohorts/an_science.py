
import logging
import warnings

import pandas

from dnm_cohorts.person import Person

url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6432922/bin/NIHMS1015808-supplement-Table1.xlsx'

def open_an_science_cohort():
    """ gets individual level data for An et al Autism dataset
    
    Table S1 from:
    An et al. Science 362: eaat6576, doi: 10.1126/science.aat6576
    """
    logging.info('getting An et al Science 2018 cohort')
    with warnings.catch_warnings():
        # suppress warning about unknown extension that doesn't affect loading data
        warnings.simplefilter("ignore")
        data = pandas.read_excel(url, sheet_name='Table S1 Sample information',
            skiprows=1, engine='openpyxl')
    data = data[['SampleID', 'FamilyID', 'Sex', 'Pheno', 'NVIQ']]
    study = ['10.1126/science.aat6576']
    
    persons = set()
    for i, row in data.iterrows():
        if row.SampleID.endswith('fa') or row.SampleID.endswith('mo'):
            # ignore parental samples
            continue
        
        status = ['unaffected'] if row.Pheno == 'control' else ['HP:0000717']
        if isinstance(row.NVIQ, int) and row.NVIQ < 70:
            status.append('HP:0001249')
        
        person = Person(row.SampleID + '|asd_cohorts', row.Sex, status, study)
        persons.add(person)
    return persons
