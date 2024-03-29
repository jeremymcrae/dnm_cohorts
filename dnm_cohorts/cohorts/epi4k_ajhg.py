
import logging
import tempfile

import pandas

from dnm_cohorts.download_file import download_file
from dnm_cohorts.person import Person
from dnm_cohorts.convert_pdf_table import extract_pages, convert_page

url = 'https://ars.els-cdn.com/content/image/1-s2.0-S0002929714003838-mmc1.pdf'


def transpose(records):
    ''' tranpose data from interpreted table columns
    
    Args:
        records: list of data per page, where each item comtains sublists of 
        data for various columns. e.g. 
            [
                ['aa ab ac', 
                 'IS IS IS', 
                 'ND1 ND2 ND3', 
                 'ND1 ND2 ND3', 
                 'ND1 ND2 ND3', 
                 'F F M', 
                 '1 1 1'
                 ], 
                 [...]
            ]
    
    Yields:
        data per row
    '''
    for page in records:
        for row in zip(*(column.split() for column in page)):
            yield row

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
        lines = [[y for y in x if y != ''] for x in lines]
        
        header, lines = lines[0], lines[1:]
        records += lines
    
    records = list(transpose(records))
    data = pandas.DataFrame.from_records(records, columns=header)
    data['person_id'] = data['Proband ID'].str.upper()
    data['sex'] = data['Proband gender'].map({'F': 'female', 'M': 'male'})
    
    return data

def open_epi4k_ajhg_cohort():
    """ gets individual level data for Epi4K cohort
    
    Supplementary Table 6 from:
    Epi4K AJHG 95: 360-370, doi: 10.1016/j.ajhg.2014.08.013
    """
    logging.info('getting EPI4K et al AJHG 2014 cohort')
    temp = tempfile.NamedTemporaryFile()
    download_file(url, temp.name)
    
    data = extract_table(temp)
    
    data['person_id'] += '|epi4k'
    status = ['HP:0001250']
    study = ['10.1016/j.ajhg.2014.08.013']
    persons = set()
    for i, row in data.iterrows():
        
        person = Person(row.person_id, row.sex, status, study)
        persons.add(person)
    
    return persons
