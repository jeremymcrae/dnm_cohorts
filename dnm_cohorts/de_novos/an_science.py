
import logging
import warnings

import pandas

from dnm_cohorts.de_novo import DeNovo

url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6432922/bin/NIHMS1015808-supplement-Table2.xlsx'

async def an_science_de_novos(result):
    """ get de novo mutations from An et al, Autism dataset
    
    Table S2 from:
    An et al. Science 362: eaat6576, doi: 10.1126/science.aat6576
    """
    logging.info('getting An et al Science 2018 de novos')
    with warnings.catch_warnings():
        # suppress warning about unknown extension that doesn't affect loading data
        warnings.simplefilter('ignore')
        data = pandas.read_excel(url, sheet_name='Table S2 de novo mutations',
            skiprows=1, usecols=list(range(8)), engine='openpyxl')
    
    data['chrom'] = data['Chr'].astype(str)
    
    data['SampleID'] += '|asd_cohorts'
    data['study'] = '10.1126/science.aat6576'
    data['confidence'] = 'high'
    
    vars = set()
    for row in data.itertuples():
        var = DeNovo(row.SampleID, row.chrom, row.Pos, row.Ref, row.Alt,
            row.study, row.confidence, 'grch38')
        vars.add(var)
    
    result.append(vars)
