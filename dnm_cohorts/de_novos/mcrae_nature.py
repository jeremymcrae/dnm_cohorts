
import pandas

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
    data['chrom'] = data['Chromosome']
    data['pos'] = data['Position (GRCh37)']
    data['ref'] = data['Reference allele']
    data['alt'] = data['Alternate allele']
    data['study'] = 'mcrae_nature_2017'
    
    qual, status = data['PP(DNM)'], data['Status']
    quality = qual.isnull() | (qual > 0.00781) | (status == 'validated')
    data['confidence'] = quality.map({True: 'high', False: 'low'})
    
    return data[['person_id', 'chrom', 'pos', 'ref', 'alt', 'study', 'confidence']]
