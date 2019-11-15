
import logging

import pandas

from dnm_cohorts.de_novo import DeNovo
from dnm_cohorts.de_novos.lelieveld_nn import fix_alleles

url = 'https://www.biorxiv.org/content/biorxiv/early/2019/10/16/797787/DC2/embed/media-2.txt'

async def kaplanis_biorxiv_de_novos(result, limiter):
    """ load de novo mutations from Kaplanis et al BioRxiv 2019
    
    These de novos are loaded from Supplementary Table 1 from
    Kaplanis et al BioRxiv 2019
    doi: 10.1101/797787
    
    Returns:
        dataframe of de novo mutations
    """
    logging.info('getting Kaplanis et al BioRxis 2019 de novos')
    data = pandas.read_table(url)
    
    data['person_id'] = data['id'] + '|' + data['study']
    data['chrom'] = data['chrom'].astype(str)
    data['study'] = '10.1101/797787'
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
