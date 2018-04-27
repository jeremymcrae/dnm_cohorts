
import pandas

from dnm_cohorts.fix_hgvs import fix_coordinates_with_allele
from dnm_cohorts.ensembl import cq_and_symbols

snv_url = 'http://www.cell.com/cms/attachment/2024816859/2044465439/mmc2.xlsx'
indel_url = 'http://www.cell.com/cms/attachment/2024816859/2044465437/mmc4.xlsx'

def get_person_ids(data):
    
    fam_ids = data['quadID'].astype(str)
    children = data.inChild.str.split('M|F')
    
    # mock up some person IDs (which are very likely to be correct)
    ids = {'aut': 'p1', 'sib': 's1'}
    
    person_ids = []
    for fam, samples in zip(fam_ids, children):
        persons = ( ids[x] for x in samples if x != '' )
        persons = [ '{}.{}'.format(fam, x) for x in persons ]
        person_ids.append(persons)
    
    return person_ids

def iossifov_neuron_de_novos():
    """ get de novo data from the 2012 Iossifov et al autism exome study in Neuron
    
    Supplementary table 1 (where the non-coding SNVs have been excluded) and
    supplementary table 2 from:
    Iossifov et al. (2012) Neuron 74:285-299
    doi: 10.1016/j.neuron.2012.04.009
    
    Returns:
        data frame of de novos, with standardised genome coordinates and VEP
        consequences for each variant.
    """
    
    snvs = pandas.read_excel(snv_url, sheet_name='SNV.v4.1-normlized')
    indels = pandas.read_excel(indel_url, sheet_name='ID.v4.1-normlized')
    
    # trim out the low quality de novos (as defined by a flag in the table)
    snvs = snvs[snvs['SNVFilter']]
    indels = indels[indels['IndelFilter']]
    
    # merge the SNV and indel de novo calls
    snvs = snvs[['quadId', 'location', 'variant', 'effectGenes', 'effectType', 'inChild']]
    indels = indels[['quadId', 'location', 'variant', 'effectGenes', 'effectType', 'inChild']]
    data = snvs.append(indels, ignore_index=False)
    
    # get the coordinates and VEP consequence
    chrom, pos, ref, alt = fix_coordinates_with_allele(data['location'], data['variant'])
    cq, symbols = cq_and_symbols(data.chrom, data.pos, data.ref, data.alt)
    data['consequence'] = cq
    data['hgnc'] = symbols
    
    data['person_id'] = get_person_ids(data)
    data['study'] = 'iossifov_neuron_2012'
    
    return data[['person_id', 'sex', 'chrom', 'pos', 'ref', 'alt', 'symbol',
        'consequence', 'study']]
