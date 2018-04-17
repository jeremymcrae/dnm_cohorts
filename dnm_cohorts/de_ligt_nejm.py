
import tempfile
import re

import pandas

from dnm_cohorts.download_file import download_file
from dnm_cohorts.person import Person
from dnm_cohorts.convert_pdf_table import extract_pages, convert_page

url = 'http://www.nejm.org/doi/suppl/10.1056/NEJMoa1206524/suppl_file/nejmoa1206524_appendix.pdf'

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
    
    temp = tempfile.NamedTemporaryFile()
    download_file(url, temp.name)
    
    data = extract_table(temp)
    
    study = 'de_ligt_nejm_2012'
    status = 'intellectual_disability'
    persons = set()
    for i, row in data.iterrows():
        person = Person(row.person_id, row.sex, status, study)
        persons.add(person)
    
    return list(persons)
