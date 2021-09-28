
import logging
import tempfile

import pandas

from dnm_cohorts.de_novo import DeNovo
from dnm_cohorts.download_file import download_file

url = 'https://www.science.org/doi/suppl/10.1126/science.aau1043/suppl_file/aau1043_datas5_revision1.tsv'

async def halldorsson_science_de_novos(result):
    """ get de novo variants for Halldorsson et al Science 2019
    
    Supplementary Data 5 (revised) from:
    Halldorsson et al. Science 343: eaau1043, doi: 10.1126/science.aau1043
    
    Halldorsson supercedes Jonsson et al, since at least 99.2% of the Jonsson et al
    samples occur in Halldorsson. See dnm_cohorts.halldorsson_check.py for more details.
    """
    logging.info('getting Halldorsson et al Science 2019 de novos')
    with tempfile.NamedTemporaryFile() as temp:
        # the url redirects, so use the requests package to open the URL
        download_file(url, temp.name)
        df = pandas.read_table(temp.name, comment='#')
    
    df['person_id'] = df['Proband_id'].astype(str)
    df['person_id'] += '|halldorsson'
    df['chrom'] = df['Chr'].astype(str)
    df['pos'] = df['Pos']
    df['ref'] = df['Ref']
    df['alt'] = df['Alt']
    df['study'] = '10.1126/science.aau1043'
    df['confidence'] = 'high'
    df['build'] = 'grch38'
    
    variants = set()
    for row in df.itertuples():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, row.build)
        variants.add(var)
    
    result.append(variants)
