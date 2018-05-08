
import re

import pandas

from dnm_cohorts.fix_hgvs import fix_coordinates_with_allele
from dnm_cohorts.de_novo import DeNovo

url = 'https://ars.els-cdn.com/content/image/1-s2.0-S0002929714003838-mmc2.xlsx'

def get_person_ids(data):
    """ lean up the person IDs
    """
    
    trios = data['TRIO ID'].str.replace('*', '').str.upper()
    person_ids = data['Child ID'].str.replace('*', '').str.upper()
    phenos = data['PHENO']
    
    # get a set of IDs that match the Coriell IDs
    # strip off the pheno and trio info
    cleaned = []
    for pheno, person_id, trio in zip(phenos, person_ids, trios):
        if person_id == trio:
            cleaned.append(person_id)
        else:
            person_id = person_id.lstrip(pheno)
            person_id = person_id.rsplit(trio, 1)[0]
            cleaned.append(person_id)
    
    # fix up one ID where the paternal ID has been used instead
    cleaned = [ x if x != 'ND29866' else 'ND29865' for x in cleaned ]
    
    return cleaned

def epi4k_ashg_de_novos():
    """ get de novo data for the Epi4K epilepsy exome study
    
    De novo mutation data from the most recent EPI4K publication:
    Supplementary table 1:
    American Journal of Human Genetics (2014) 95:360-370
    doi: 10.1016/j.ajhg.2014.08.013
    
    This incorporates the de novo mutation data from supplementary table 2 of:
    Allen et al. (2013) Nature 501:217-221
    doi: 10.1038/nature12439
    
    Returns:
        data.frame of de novo mutations
    """
    data = pandas.read_excel(url, skip_footer=4)
    
    data['chrom'], data['pos'], data['ref'], data['alt'] = fix_coordinates_with_allele( \
        data['hg19 coordinates (chr:position)'], data["Ref/Alt alleles"])
    
    data['study'] = "10.1016/j.ajhg.2014.08.013"
    
    data['person_id'] = get_person_ids(data)
    data['person_id'] += '|epi4k'
    data['confidence'] = 'high'
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence)
        vars.add(var)
    
    return vars
