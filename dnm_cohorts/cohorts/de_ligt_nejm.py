
import logging
import re
import tempfile

import pandas

from dnm_cohorts.download_file import download_file
from dnm_cohorts.person import Person
from dnm_cohorts.convert_pdf_table import extract_pages, convert_page

# I would prefer to use a NEJM URL, but the NEJM website requires accessing via 
# a javascript enabled browser to authenticate the request. I stashed the same 
# file in a google bucket instead.
# url = 'https://www.nejm.org/doi/suppl/10.1056/NEJMoa1206524/suppl_file/nejmoa1206524_appendix.pdf'
url = 'https://storage.googleapis.com/6cf434c4c71ee9c3cf1b2d8cfc0e9cd32e8d1e64/nejmoa1206524_appendix.pdf'

def extract_table(handle):
    
    records = []
    for page in extract_pages(handle, start=4, end=26):
        data = convert_page(page)
        
        data = sorted(data, reverse=True, key=lambda x: x.y0)
        for line in data:
            text = [ x.get_text() for x in sorted(line, key=lambda x: x.x0) ]
            text = ''.join(text)
            records.append(text)
    
    male = re.compile('[Tt]his (boy|male)+')
    female = re.compile('[Tt]his (girl|female)+')
    ids, sex = [], []
    for line in records:
        if line.startswith('Trio'):
            ids.append(line.split(' ')[1])
            if male.search(line) is not None:
                sex.append('male')
            elif female.search(line) is not None:
                sex.append('female')
            else:
                # Trio 69 only refers to 'she'.
                sex.append('female')
    
    return pandas.DataFrame({'person_id': ids, 'sex': sex})

def open_de_ligt_cohort():
    """ get individuals from De Ligt et al., 2012
    
    De Ligt et al., (2012) N Engl J Med 367:1921-1929
    doi:10.1056/NEJMoa1206524
    Proband details sourced from 'Clinical description of patients' section in
    supplementary material.
    """
    logging.info('getting De Ligt et al NEJM 2012 cohort')
    temp = tempfile.NamedTemporaryFile()
    download_file(url, temp.name)
    
    data = extract_table(temp)
    data['person_id'] += '|de_ligt'
    
    status = ['HP:0001249']
    study = ['10.1056/NEJMoa1206524']
    persons = set()
    for i, row in data.iterrows():
        person = Person(row.person_id, row.sex, status, study)
        persons.add(person)
    
    return persons
