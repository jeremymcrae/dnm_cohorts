

import pandas

from dnm_cohorts.ensembl import cq_and_symbols

url = 'https://www.cell.com/cms/attachment/2118908541/2086568191'

def sanders_neuron():
    """ get de novo data from the Sanders et al Neuron autism exome study
    
    Supplementary table 5 from:
    Sanders et al. (2015) Neuron 87:1215-1233
    doi: 10.1016/j.neuron.2015.09.016
    
    Returns:
        data frame of de novos, with standardised genome coordinates and VEP
        consequences for each variant
    """
    
    data = pandas.read_excel(url, sheet_name='Exome')
    
    data['person_id'] = data['patientID']
    data['chrom'] = data['Chr']
    data['pos'] = data['Pos(hg19)']
    data['ref'] = data['Ref']
    data['alt'] = data['Alt']
    
    cqs, symbols = cq_and_symbols(data.chrom, data.pos, data.ref, data.alt)
    data['consequence'] = cqs
    data['symbol'] = symbols
    
    data['study'] = "sanders_neuron_2015"
    
    return data[['person_id','chrom', 'pos', 'ref', 'alt', 'symbol',
        'consequence', 'study']]
