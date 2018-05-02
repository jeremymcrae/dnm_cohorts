
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
        data = convert_page(page)
        
        data = sorted(data, reverse=True, key=lambda x: x.y0)
        data = data[1:]
        header, data = data[0], data[1:]
        for line in data:
            text = [ x.get_text() for x in sorted(line, key=lambda x: x.x0) ]
            records.append(text)
    
    header = [ x.get_text() for x in sorted(header, key=lambda x: x.x0) ]
    
    data = pandas.DataFrame.from_records(records, columns=header)
    data['person_id'] = data['Patient ID']
    data['sex'] = data['Gender'].map({'f': 'female', 'm': 'male'})
    
    return data

def open_rauch_cohort():
    
    temp = tempfile.NamedTemporaryFile()
    download_file(url, temp.name)
    
    data = extract_table(temp)
    data['person_id'] += '|rauch'
    
    status = 'intellectual_disability'
    persons = set()
    for i, row in data.iterrows():
        
        person = Person(row.person_id, row.sex, status)
        persons.add(person)
    
    return persons
