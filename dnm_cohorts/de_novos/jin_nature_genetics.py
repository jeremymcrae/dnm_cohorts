
import logging

import pandas

from dnm_cohorts.de_novo import DeNovo

url = 'https://media.nature.com/original/nature-assets/ng/journal/v49/n11/extref/ng.3970-S3.xlsx'

async def jin_nature_genetics_de_novos(result):
    """ gets individual level data for Jin et al congenital heart disease
    
    Supplementary Table 9 from:
    Jin et al. Nature Genetics 49: 1593-1601, doi: 10.1038/ng.3970
    """
    logging.info('getting Jin et al Nature Genetics 2017 de novos')
    data = pandas.read_excel(url, 'S9', skiprows=1)
    data['person_id'] = data['Blinded ID'].astype(str) + '|jin'
    
    data['chrom'] = data['CHROM'].astype(str)
    data['pos'] = data['POS']
    data['ref'] = data['REF']
    data['alt'] = data['ALT']
    data['study'] = '10.1038/ng.3970'
    data['confidence'] = 'high'
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, 'grch37')
        vars.add(var)
    
    result.append(vars)
