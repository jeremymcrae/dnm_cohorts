
import pandas

from dnm_cohorts.de_novo import DeNovo

url = 'http://www.nature.com/nature/journal/v542/n7642/extref/nature21062-s2.xlsx'

def mcrae_nature_de_novos():
    """ load de novo mutations from McRae et al Nature 2017
    
    These de novos are loaded from Supplementary Table 1 from
    McRae et al Nature 2017 542:433-438
    doi: 10.1038/nature21062
    
    Returns:
        dataframe of de novo mutations
    """
    data = pandas.read_excel(url, sheet_name='Supplementary Table 1')
    
    data['person_id'] = data['Individual ID']
    data['chrom'] = data['Chromosome'].astype(str)
    data['pos'] = data['Position (GRCh37)']
    data['ref'] = data['Reference allele']
    data['alt'] = data['Alternate allele']
    
    data['person_id'] += '|DDD'
    data['study'] = '10.1038/nature21062'
    
    qual, status = data['PP(DNM)'], data['Status']
    quality = qual.isnull() | (qual > 0.00781) | (status == 'validated')
    data['confidence'] = quality.map({True: 'high', False: 'low'})
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence)
        vars.add(var)
    
    return vars
