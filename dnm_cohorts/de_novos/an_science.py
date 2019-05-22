
import pandas

from dnm_cohorts.de_novo import DeNovo

url = 'https://science.sciencemag.org/highwire/filestream/720071/field_highwire_adjunct_files/2/aat6576_Table-S2.xlsx'

def an_science_de_novos():
    """ get de novo mutations from An et al, Autism dataset
    
    Table S2 from:
    An et al. Science 362: eaat6576, doi: 10.1126/science.aat6576
    """
    
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
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, 'grch38', row.consequence, row.symbol)
        vars.add(var)
    
    return vars