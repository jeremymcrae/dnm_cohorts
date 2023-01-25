
import logging

import pandas

from dnm_cohorts.fix_hgvs import fix_coordinates_with_allele
from dnm_cohorts.de_novos.iossifov_nature import tidy_families
from dnm_cohorts.de_novo import DeNovo

snv_url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3619976/bin/NIHMS374246-supplement-02.xlsx'
indel_url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3619976/bin/NIHMS374246-supplement-04.xlsx'

def get_person_ids(data):
    
    fam_ids = data['quadId'].astype(str)
    children = data.inChild.str.split('M|F')
    
    # mock up some person IDs (which are very likely to be correct)
    ids = {'aut': 'p1', 'sib': 's1'}
    
    person_ids = []
    for fam, samples in zip(fam_ids, children):
        persons = ( ids[x] for x in samples if x != '' )
        persons = [ f'{fam}.{x}' for x in persons ]
        person_ids.append(persons)
    
    return person_ids

async def iossifov_neuron_de_novos(result, limiter):
    """ get de novo data from the 2012 Iossifov et al autism exome study in Neuron
    
    Supplementary table 1 (where the non-coding SNVs have been excluded) and
    supplementary table 2 from:
    Iossifov et al. (2012) Neuron 74:285-299
    doi: 10.1016/j.neuron.2012.04.009
    
    Returns:
        data frame of de novos, with standardised genome coordinates and VEP
        consequences for each variant.
    """
    logging.info('getting Iossifov et al Neuron 2012 de novos')
    snvs = pandas.read_excel(snv_url, sheet_name='SNV.v4.1-normlized')
    indels = pandas.read_excel(indel_url, sheet_name='ID.v4.1-normlized')
    
    # trim out the low quality de novos (as defined by a flag in the table)
    snvs = snvs[snvs['SNVFilter']]
    indels = indels[indels['IndelFilter']]
    
    # merge the SNV and indel de novo calls
    snvs = snvs[['quadId', 'location', 'variant', 'effectGenes', 'effectType', 'inChild']]
    indels = indels[['quadId', 'location', 'variant', 'effectGenes', 'effectType', 'inChild']]
    data = pandas.concat([snvs, indels], ignore_index=True)
    
    # get the coordinates
    coords = await fix_coordinates_with_allele(limiter, data['location'], data['variant'])
    data['chrom'], data['pos'], data['ref'], data['alt'] = coords
    
    data['person_id'] = get_person_ids(data)
    data = tidy_families(data)
    
    data['person_id'] += '|asd_cohorts'
    data['study'] = '10.1016/j.neuron.2012.04.009'
    data['confidence'] = 'high'
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, 'grch37')
        vars.add(var)
    
    result.append(vars)
