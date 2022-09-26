
import logging
import tempfile

import pandas

from dnm_cohorts.download_file import download_file
from dnm_cohorts.person import Person
from dnm_cohorts.convert_pdf_table import extract_pages, convert_page

url = 'https://ars.els-cdn.com/content/image/1-s2.0-S0140673612614809-mmc1.pdf'

def extract_table(handle):
    
    records = []
    header = None
    for page in extract_pages(handle, start=12, end=16):
        data = convert_page(page, delta=2.7)
        
        data = sorted(data, reverse=True, key=lambda x: x.y0)
        data = data[1:]
        header, data = data[0], data[1:]
        for line in data:
            text = [ x.get_text() for x in sorted(line, key=lambda x: x.x0) ]
            if len(text) > 10:
                records.append(text)
    
    header = [ x.get_text() for x in sorted(header, key=lambda x: x.x0) ]
    
    data = pandas.DataFrame.from_records(records, columns=header)
    data['person_id'] = data['Patient ID'].str.replace('‐', '-')
    data['sex'] = data['Gender'].map({'f': 'female', 'm': 'male'})
    
    # fix one person ID which doesn't match the ID for its de novos
    data['person_id'][43] = 'TUTLN'
    
    return data

def open_rauch_cohort():
    """ get person data for Rauch et al. intellectual disability exome study
    
     Rauch et al. (2012) Lancet 380:1674-1682
     doi: 10.1016/S0140-6736(12)61480-9
     Supplementary table 1
    """
    logging.info('getting Rauch et al Lancet 2012 cohort')
    temp = tempfile.NamedTemporaryFile()
    download_file(url, temp.name)
    
    data = extract_table(temp)
    data['person_id'] += '|rauch'
    
    status = ['HP:0001249']
    study = ['10.1016/S0140-6736(12)61480-9']
    persons = set()
    for i, row in data.iterrows():
        
        person = Person(row.person_id, row.sex, status, study)
        persons.add(person)
    
    return persons
