
import pandas

from dnm_cohorts.de_novo import DeNovo

url = 'https://www.cell.com/cms/attachment/2118908541/2086568191'

def sanders_neuron_de_novos():
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
    data['study'] = "sanders_neuron_2015"
    
    quality = data['Confidence'] != 'lowConf'
    data['confidence'] = quality.map({True: 'high', False: 'low'})
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence)
        vars.add(var)
    
    return vars
