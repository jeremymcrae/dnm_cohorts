
import logging

import pandas

from dnm_cohorts.de_novo import DeNovo

url = 'https://static-content.springer.com/esm/art%3A10.1038%2Fnature21062/MediaObjects/41586_2017_BFnature21062_MOESM34_ESM.xlsx'

async def mcrae_nature_de_novos(result):
    """ load de novo mutations from McRae et al Nature 2017
    
    These de novos are loaded from Supplementary Table 1 from
    McRae et al Nature 2017 542:433-438
    doi: 10.1038/nature21062
    
    Returns:
        dataframe of de novo mutations
    """
    logging.info('getting McRae et al Nature 2017 de novos')
    data = pandas.read_excel(url, sheet_name='Supplementary Table 1')
    
    data['person_id'] = data['Individual ID']
    data['chrom'] = data['Chromosome'].astype(str)
    data['pos'] = data['Position (GRCh37)']
    data['ref'] = data['Reference allele']
    data['alt'] = data['Alternate allele']
    
    data['person_id'] += '|DDD'
    data['study'] = '10.1038/nature21062'
    
    qual, status = data['PP(DNM)'], data['Status']
    quality = qual.isnull() | (qual > 0.00781) | (status == 'validated')
    data['confidence'] = quality.map({True: 'high', False: 'low'})
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, 'grch37')
        vars.add(var)
    
    result.append(vars)
