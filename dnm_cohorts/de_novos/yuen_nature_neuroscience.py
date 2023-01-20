
import logging

import pandas

from dnm_cohorts.de_novo import DeNovo

url = 'https://static-content.springer.com/esm/art%3A10.1038%2Fnn.4524/MediaObjects/41593_2017_BFnn4524_MOESM49_ESM.xlsx'

async def yuen_nature_neuroscience_de_novos(result):
    """ gets individual level data for Yuen et al 2017
    
    Supplementary Table 3 from:
    Yuen et al. Nature Neturoscience 2017, 20:602-611
    doi: 10.1038/nn.4524
    """
    logging.info('getting Yuen et al Nature Neuroscience 2017 de novos')
    data = pandas.read_excel(url, 'Table S3', skiprows=1)
    
    data['person_id'] = data['SAMPLE']
    data['chrom'] = data['CHROM']
    data['pos'] = data['START'] + 1  # this dataset used zero-based coords
    data['ref'] = data['REF']
    data['alt'] = data['ALT']
    data['study'] = '10.1038/nn.4524'
    data['confidence'] = 'high'
    
    variants = set()
    for row in data.itertuples():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, 'grch37')
        variants.add(var)
    
    result.append(variants)
