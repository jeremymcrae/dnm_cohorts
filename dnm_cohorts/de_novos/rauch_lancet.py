
import logging
import tempfile

import pandas

from dnm_cohorts.download_file import download_file
from dnm_cohorts.convert_pdf_table import extract_pages, convert_page
from dnm_cohorts.fix_hgvs import fix_hgvs_coordinates
from dnm_cohorts.de_novo import DeNovo

url = 'https://ars.els-cdn.com/content/image/1-s2.0-S0140673612614809-mmc1.pdf'

def extract_table_s2(handle):
    """ get the table of nonsynonymous de novos
    """
    
    records = []
    for page in extract_pages(handle, start=20, end=22):
        data = convert_page(page, delta=1)
        
        data = sorted(data, reverse=True, key=lambda x: x.y0)
        lines = []
        for line in data:
            text = [ x.get_text().strip() for x in sorted(line, key=lambda x: x.x0) ]
            lines.append(text)
        
        # drop the page number line, blank lines, and only use a few entries
        lines = ( x for x in lines if x != [''] )
        lines = ( x for x in lines if len(x) > 2 )
        lines = [ x[:4] for x in lines ]
        
        records += lines
    
    records.pop(0)
    records.pop(-1)
    
    # fix the last line
    records[-1] = [ x.split('\xa0')[0] for x in records[-1] ]
    
    # fix a scrambled pair of lines
    mixed = records.pop(-2)
    records += map(list, zip(*[x.split('\xa0') for x in mixed ]))
    
    header = ['person_id', 'symbol', 'cq', 'hgvs_genomic']
    return pandas.DataFrame.from_records(records, columns=header)

def extract_table_s3(handle):
    """ get the table of synonymous de novos
    """
    
    records = []
    for page in extract_pages(handle, start=23, end=24):
        data = convert_page(page, delta=1)
        
        data = sorted(data, reverse=True, key=lambda x: x.y0)
        lines = []
        for line in data:
            text = [ x.get_text().strip() for x in sorted(line, key=lambda x: x.x0) ]
            lines.append(text)
        
        # drop the page number line, blank lines, and only use a few entries
        lines = ( x for x in lines if x != [''] )
        lines = ( x for x in lines if len(x) > 2 )
        lines = [ x[:3] for x in lines ]
        
        records += lines
    
    # drop the last few rows
    records = records[:-4]
    
    # fix a scrambled pair of lines
    mixed = records.pop(6)
    records += map(list, zip(*[x.split('\xa0') for x in mixed ]))
    
    header = ['person_id', 'symbol', 'hgvs_genomic']
    return pandas.DataFrame.from_records(records, columns=header)

async def rauch_lancet_de_novos(result, limiter):
    """ get de novo data for Rauch et al. intellectual disability exome study
    
     De novo mutation data sourced from supplementary tables 2 and 3 from
     Rauch et al. (2012) Lancet 380:1674-1682
     doi: 10.1016/S0140-6736(12)61480-9
    
    Returns:
        data frame of de novos, including gene symbol, functional consequence
        (VEP format), chromosome, nucleotide position
    """
    logging.info('getting Rauch et al Lancet 2012 de novos')
    # obtain the supplementary material
    temp = tempfile.NamedTemporaryFile()
    download_file(url, temp.name)
    
    s2 = extract_table_s2(temp)
    del s2['cq']
    s3 = extract_table_s3(temp)
    data = s2.append(s3, ignore_index=True)
    
    coords = await fix_hgvs_coordinates(limiter, data['hgvs_genomic'])
    data['chrom'], data['pos'], data['ref'], data['alt'] = coords
    
    # define the study details
    data['person_id'] += '|rauch'
    data['person_id'] = data['person_id'].str.replace('‐', '-')
    data['study'] = "10.1016/S0140-6736(12)61480-9"
    data['confidence'] = 'high'
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, 'grch37')
        vars.add(var)
    
    result.append(vars)
