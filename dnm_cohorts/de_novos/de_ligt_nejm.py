

import tempfile
import re

import pandas

from dnm_cohorts.download_file import download_file
from dnm_cohorts.person import Person
from dnm_cohorts.convert_pdf_table import extract_pages, convert_page
from dnm_cohorts.fix_hgvs import fix_hgvs_coordinates

url = 'http://www.nejm.org/doi/suppl/10.1056/NEJMoa1206524/suppl_file/nejmoa1206524_appendix.pdf'

def extract_table(handle):
    
    records = []
    for page in extract_pages(handle, start=41, end=44):
        data = convert_page(page)
        
        data = sorted(data, reverse=True, key=lambda x: x.y0)
        lines = []
        for line in data:
            text = [ x.get_text().strip() for x in sorted(line, key=lambda x: x.x0) ]
            lines.append(text)
        
        if lines[0][0].startswith('Table S3'):
            lines = lines[1:]
        
        # drop the page number line, blank lines, and only use a few entries
        lines = lines[:-1]
        lines = ( x for x in lines if x != [''] )
        lines = [ x[:5] for x in lines ]
        
        # drop the final key line
        if lines[-1][0].startswith('K: Known'):
            lines = lines[:-1]
        
        records += lines
    
    header, records = records[0], records[1:]
    return pandas.DataFrame.from_records(records, columns=header)

def clean_table(data):
    
    # rename some columns
    data = data.rename(columns={'Trio': 'person_id', 'Gene': 'symbol',
         'Genomic position': 'hgvs_genomic'})
    
    # fix the hgvs genomic string
    pat = re.compile("\(GRC[h|H]37\):*g")
    data.hgvs_genomic = data.hgvs_genomic.str.replace(pat, ":g")
    data.hgvs_genomic = data.hgvs_genomic.str.replace('Chr', "chr")
    data.hgvs_genomic = data.hgvs_genomic.str.replace('-', "_")
    
    # convert a position with NCBI36 genome assembly coordinates
    data.hgvs_genomic[26] = "chr19:g.53958839G>C"
    
    return data

def open_de_ligt():
    
    temp = tempfile.NamedTemporaryFile()
    download_file(url, temp.name)
    
    data = extract_table(temp)
    data = clean_table(data)
    
    chrom, pos, ref, alt = fix_hgvs_coordinates(data.hgvs_genomic)
    data['chrom'], data['pos'], data['ref'], data['alt'] = chrom, pos, ref, alt
    
    data['study'] = "deligt_nejm_2012"
    
    return data[['person_id', 'chrom', 'pos', 'ref', 'alt', 'study']]
