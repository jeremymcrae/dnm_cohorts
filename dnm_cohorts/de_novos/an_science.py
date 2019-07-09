
import logging

import pandas

from dnm_cohorts.de_novo import DeNovo

url = 'https://science.sciencemag.org/content/sci/suppl/2018/12/12/362.6420.eaat6576.DC1/aat6576_Table-S2.xlsx'

def an_science_de_novos():
    """ get de novo mutations from An et al, Autism dataset
    
    Table S2 from:
    An et al. Science 362: eaat6576, doi: 10.1126/science.aat6576
    """
    logging.info('getting An et al Science 2018 de novos')
    data = pandas.read_excel(url, sheet_name='Table S2 de novo mutations', skiprows=1)
    
    data['person_id'] = data['SampleID']
    data['chrom'] = data['Chr'].astype(str)
    data['pos'] = data['Pos']
    data['ref'] = data['Ref']
    data['alt'] = data['Alt']
    data['consequence'] = data['Consequence']
    data['symbol'] = data['SYMBOL']
    
    data['person_id'] += '|asd_cohorts'
    data['study'] = '10.1126/science.aat6576'
    data['confidence'] = 'high'
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.SampleID, row.chrom, row.Pos, row.Ref, row.Alt,
            row.study, row.confidence, 'grch38')
        vars.add(var)
    
    return vars
