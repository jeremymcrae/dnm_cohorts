
import logging

import pandas

from dnm_cohorts.de_novo import DeNovo
from dnm_cohorts.cohorts.fu_nature_genetics import clean_ssc_ids

url = 'https://static-content.springer.com/esm/art%3A10.1038%2Fs41588-022-01104-0/MediaObjects/41588_2022_1104_MOESM3_ESM.xlsx'

async def fu_nature_genetics_de_novos(result):
    """ gets individual level data for Fu et al
    
    Supplementary Table 20 from:
    Fu et al. Nature Genetics 2022, doi: 10.1038/s41588-022-01104-0
    """
    logging.info('getting Fu et al Nature Genetics 2022 de novos')
    data = pandas.read_excel(url, 'Supplementary Table 20', skipfooter=18)
    sample_df = pandas.read_excel(url, 'Supplementary Table 4', skipfooter=14)
    sample_df['person_id'] = sample_df['Sample'].astype(str) + '|asd_cohorts'
    sample_df['person_id'] = clean_ssc_ids(sample_df)
    
    data['person_id'] = data['Sample'].map(dict(zip(sample_df.Sample, sample_df.person_id)))
    
    data[['chrom', 'pos', 'ref', 'alt']] = data['Variant'].str.split(':', expand=True)
    data['pos'] = data['pos'].astype(int)
    data['study'] = '10.1038/s41588-022-01104-0'
    data['confidence'] = 'high'
    
    variants = set()
    for row in data.itertuples():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, 'grch38')
        variants.add(var)
    
    result.append(variants)
