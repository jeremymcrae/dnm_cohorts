
import re

import pandas

from dnm_cohorts.fix_hgvs import fix_coordinates_with_allele
from dnm_cohorts.de_novo import DeNovo

url = 'https://ars.els-cdn.com/content/image/1-s2.0-S0002929714003838-mmc2.xlsx'

#' get de novo data for the Epi4K epilepsy exome study
#'
#' De novo mutation data from the most recent EPI4K publication:
#' Supplementary table 1:
#' American Journal of Human Genetics (2014) 95:360-370
#' doi: 10.1016/j.ajhg.2014.08.013
#'
#' This incorporates the de novo mutation data from supplementary table 2 of:
#' Allen et al. (2013) Nature 501:217-221
#' doi: 10.1038/nature12439
#'
#' @export
#'
#' @return data frame of de novos, including gene symbol, functional consequence
#'     (VEP format), chromosome, nucleotide position and SNV or INDEL type
def epi4k_ashg_de_novos():
    
    data = pandas.read_excel(url, skip_footer=4)
    
    data['chrom'], data['pos'], data['ref'], data['alt'] = fix_coordinates_with_allele( \
        data['hg19 coordinates (chr:position)'], data["Ref/Alt alleles"])
    
    data['TRIO ID'] = data['TRIO ID'].str.replace('*', '')
    data['person_id'] = data['Child ID'].str.replace('*', '').str.upper()
    
    data['study'] = "epi4k_ajhg_2014"
    
    # get a set of IDs that match the Coriell IDs
    pat = re.compile("ND[0-9]*")
    person_ids = list(data.person_id)
    matches = ( pat.search(x) for x in person_ids )
    person_ids = [ m.group() if m is not None else person_ids[i] for i, m in enumerate(matches) ]
    
    data['person_id'] = person_ids
    data['confidence'] = 'high'
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence)
        vars.add(var)
    
    return vars
