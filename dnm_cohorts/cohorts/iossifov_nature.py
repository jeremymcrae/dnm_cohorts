
import logging
import os
import tempfile
import math
from zipfile import ZipFile

import pandas

from dnm_cohorts.person import Person
from dnm_cohorts.download_file import download_file

url = 'https://static-content.springer.com/esm/art%3A10.1038%2Fnature13908/MediaObjects/41586_2014_BFnature13908_MOESM117_ESM.zip'

def get_members(row):
    '''get the member IDs from the sequencing center columns
    '''
    columns = ['SequencedAtCSHL', 'SequencedAtUW', 'SequencedAtYALE']
    for col in columns:
        value = row[col]
        if type(value) != str:
            continue
        for member in value.split(','):
            yield member

def open_iossifov_nature_cohort():
    """ get proband details fromn Iossifov et al., Nature 2014
    
    Nature (2014) 515: 216-221, doi:10.1038/nature13908
    Supplementary table S1.
    """
    logging.info('getting Iossifov et al Nature 2014 cohort')
    tempdir = tempfile.TemporaryDirectory()
    zipf = os.path.join(tempdir.name, 'temp.zip')
    download_file(url, zipf)
    
    with ZipFile(zipf) as zipped:
        zipped.extractall(tempdir.name)
    
    path = os.path.join(tempdir.name, 'nature13908-s2', 'Supplementary Table 1.xlsx')
    data = pandas.read_excel(path, 'Supplement-T1-familiesTable')
    study = ['10.1038/nature13908']
    
    persons = set()
    for i, row in data.iterrows():
        
        fam = row.familyId
        for member in get_members(row):
            sex = row['probandGender'] if member[0] == 'p' else row['siblingGender']
            
            status = ['HP:0000717'] if member[0] == 'p' else ['unaffected']
            if member[0] == 'p' and (row.probandVIQ < 70 or row.probandNVIQ < 70):
                status.append('HP:0001249')
            sex = 'male' if sex == 'M' else 'female'
            person_id = f'{fam}.{member}|asd_cohorts'
            
            person = Person(person_id, sex, status, study)
            persons.add(person)
    
    return persons
