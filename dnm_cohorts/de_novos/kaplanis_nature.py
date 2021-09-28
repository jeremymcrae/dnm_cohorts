
import logging

import pandas

from dnm_cohorts.de_novo import DeNovo
from dnm_cohorts.de_novos.lelieveld_nn import fix_alleles

url = 'https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-020-2832-5/MediaObjects/41586_2020_2832_MOESM3_ESM.txt'

async def kaplanis_nature_de_novos(result, limiter):
    """ load de novo mutations from Kaplanis et al Nature 2020
    
    These de novos are loaded from Supplementary Table 1 from
    Kaplanis et al Nature 2020
    doi: 10.1038/s41586-020-2832-5
    
    Returns:
        dataframe of de novo mutations
    """
    logging.info('getting Kaplanis et al Nature 2019 de novos')
    data = pandas.read_table(url)
    
    data['person_id'] = data['id'] + '|' + data['study']
    data['chrom'] = data['chrom'].astype(str)
    data['study'] = '10.1038/s41586-020-2832-5'
    data['confidence'] = 'high'
    data['build'] = 'grch37'
    
    # fix RUMC indels, as insertions lack ref alleles and deletions lack alts
    data['ref'], data['alt'] = await fix_alleles(limiter, data)
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, row.build)
        vars.add(var)
    
    result.append(vars)
