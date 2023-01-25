
import logging

import pandas

from dnm_cohorts.de_novo import DeNovo

url = "https://static-content.springer.com/esm/art%3A10.1038%2Fnature13772/MediaObjects/41586_2014_BFnature13772_MOESM41_ESM.xlsx"

async def de_rubeis_nature_de_novos(result):
    """ get de novo data from the 2014 De Rubeis et al. autism exome study in Nature
    
    De novo mutation data sourced from Supplementary table 3:
    De Rubeis et al. (2013) Nature 515:209-215
    doi: 10.1038/nature13772
    
    Returns:
        data frame of de novos, including gene symbol, functional consequence
         (VEP format), chromosome, nucleotide position
    """
    
    logging.info('getting De Rubeis et al Nature 2013 de novos')
    data = pandas.read_excel(url, sheet_name="De Novo", skipfooter=1)
    
    # rename columns to match the other de novo datasets
    data = data.rename(columns={'Chr': 'chrom', 'Pos': 'pos',
        'Child_ID': 'person_id', 'Ref': 'ref', 'Alt': 'alt'})
    
    # strip whitespace and ensure columns are string
    for col in ['person_id', 'chrom', 'ref', 'alt']:
        data[col] = data[col].astype(str).str.replace(' |\t', '', regex=False)
    
    data['person_id'] += '|asd_cohorts'
    data['study'] = "10.1038/nature13772"
    data['confidence'] = 'high'
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, 'grch37')
        vars.add(var)
    
    result.append(vars)
