
import os
import random
import tempfile
from zipfile import ZipFile

import pandas

from dnm_cohorts.download_file import download_file
from dnm_cohorts.person import Person

url = 'http://science.sciencemag.org/highwire/filestream/646355/field_highwire_adjunct_files/1/aac9396_SupportingFile_Other_seq1_v4.zip'

def open_homsy_science_cohort():
    """ gets individual level data for Homsy et al congenital heart disease
    
    Supplementary Database 1 from:
    Homsy et al. Science 350: 1262-1266, doi: 10.1126/science.aac9396
    """
    random.seed(1)
    zipf = tempfile.NamedTemporaryFile()
    download_file(url, zipf.name)
    
    with ZipFile(zipf.name) as zipped:
        handle = zipped.open('homsy_database_S01.xlsx')
        data = pandas.read_excel(handle, 'Database S1', skiprows=1)
    
    data = data.drop(0, axis=0)
    data = data.rename(columns={
        'NDD determination if PCGC cohort': 'Developmental Delay',
        'Unnamed: 6': 'Learning Disability',
        'Unnamed: 7': 'Mental Retardation',
        'Unnamed: 8': 'Autism Spectrum'})
    
    data['person_id'] = data['Blinded ID']
    data['person_id'] += '|homsy'
    
    # estimate male fraction from proportion in Zaidi et al 2013, since the
    # sex isn't provided for individuals, nor the count of people per sex.
    male_fraction = 220 / (220 + 142)
    
    persons = set()
    for i, row in data.iterrows():
        status = ['HP:0001627']
        sex = 'male' if random.random() < male_fraction else 'female'
        if row['Developmental Delay'] == 'Yes':
            status.append('HP:0001263')
        if row['Mental Retardation'] == 'Yes':
            status.append('HP:0001249')
        if row['Autism Spectrum'] == 'Yes':
            status.append('HP:0000717')
        
        person = Person(row.person_id, sex, status)
        persons.add(person)
    
    return persons
