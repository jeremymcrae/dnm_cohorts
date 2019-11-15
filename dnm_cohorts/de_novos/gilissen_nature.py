
import logging
import tempfile
import re

import pandas

from dnm_cohorts.download_file import download_file
from dnm_cohorts.person import Person
from dnm_cohorts.convert_pdf_table import extract_pages, convert_page
from dnm_cohorts.fix_hgvs import fix_hgvs_coordinates
from dnm_cohorts.de_novo import DeNovo

url = 'http://www.nature.com/nature/journal/v511/n7509/extref/nature13394-s1.pdf'

def extract_table(handle):
    
    records = []
    for page in extract_pages(handle, start=33, end=37):
        data = convert_page(page, delta=0.5)
        
        data = sorted(data, reverse=True, key=lambda x: x.y0)
        lines = []
        for line in data:
            text = [ x.get_text().strip() for x in sorted(line, key=lambda x: x.x0) ]
            lines.append(text)
        
        if lines[0][0].startswith('Supplementary Table 8'):
            lines = lines[1:]
        
        # drop the footer lines and lines with too few entries
        lines = lines[:-2]
        lines = [ x for x in lines if len(x) > 2 ]
        
        records += lines
    
    # tidy up two consecutive lines, where the person ID has gone astray
    records[20][0] = '9'
    records[21].insert(0, '9')
    
    # remove the final few footer lines
    records = records[:-5]
    
    # standardise the columns
    records = [ x[:5] for x in records ]
    
    header, records = records[0], records[1:]
    return pandas.DataFrame.from_records(records, columns=header)

def clean_table(data):
    
    # rename some columns
    data = data.rename(columns={'Trio': 'person_id', 'Gene': 'symbol',
         'Genomic annotation': 'hgvs_genomic'})
    
    # fix the hgvs genomic string
    pat = re.compile("\(GRC[h|H]37\):*g")
    data.hgvs_genomic = data.hgvs_genomic.str.replace(pat, ':g')
    data.hgvs_genomic = data.hgvs_genomic.str.replace('Chr', 'chr')
    data.hgvs_genomic = data.hgvs_genomic.str.replace(' ', '')
    
    return data

async def gilissen_nature_de_novos(result, limiter):
    """ load de novos from Gilissen et al Nature 2014
    
    Nature 511: 344-347 2014, doi:10.1038/nature13394
    Supplementary table S8.
    """
    logging.info('getting Gilissen et al Nature 2014 de novos')
    temp = tempfile.NamedTemporaryFile()
    download_file(url, temp.name)
    
    data = extract_table(temp)
    data = clean_table(data)
    
    chrom, pos, ref, alt = await fix_hgvs_coordinates(limiter, data.hgvs_genomic)
    data['chrom'], data['pos'], data['ref'], data['alt'] = chrom, pos, ref, alt
    
    data['person_id'] += '|de_ligt'
    data['study'] = '10.1038/nature13394'
    data['confidence'] = 'high'
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, 'grch37')
        vars.add(var)
    
    result.append(vars)
