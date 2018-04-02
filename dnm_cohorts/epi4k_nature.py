
import tempfile

import pandas

from dnm_cohorts.download_file import download_file
from dnm_cohorts.hashdict import Hashdict
from dnm_cohorts.convert_pdf_table import extract_pages, convert_page

url = 'https://media.nature.com/original/nature-assets/nature/journal/v501/n7466/extref/nature12439-s1.pdf'
url = 'http://www.cell.com/cms/attachment/2018960629/2039173309/mmc1.pdf'

def extract_table(handle):
    
    records = []
    header = None
    for page in extract_pages(handle, start=17, end=26):
        data = convert_page(page, delta=3)
        
        data = sorted(data, reverse=True, key=lambda x: x.y0)
        
        lines = []
        for line in data:
            text = [ x.get_text().strip() for x in sorted(line, key=lambda x: x.x0) ]
            lines.append(text)
        
        # drop any table legends
        while lines:
            if lines[0][0].startswith('Family'):
                break
            lines = lines[1:]
        
        # drop the page number line
        lines = lines[:-1]
        
        # drop blank lines
        lines = [ x for x in lines if x != [''] ]
        
        header, lines = lines[0], lines[1:]
        records += lines
    
    data = pandas.DataFrame.from_records(records, columns=header)
    data['person_id'] = data['Proband ID']
    data['sex'] = data['Proband gender'].map({'F': 'female', 'M': 'male'})
    
    return data

def open_epi4k_nature_cohort():
    
    temp = tempfile.NamedTemporaryFile()
    download_file(url, temp.name)
    
    data = extract_table(temp)
    
    study = 'epi4k_ajhg_2014'
    status = 'seizures'
    persons = set()
    for i, row in data.iterrows():
        
        person = Hashdict({'person_id': row.person_id, 'sex': row.sex,
            'phenotype': status, 'study': study})
        persons.add(person)
    
    return list(persons)
