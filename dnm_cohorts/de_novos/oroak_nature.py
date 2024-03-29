
import trio
import logging

import pandas

from dnm_cohorts.ensembl import parallel_sequence
from dnm_cohorts.fix_alleles import fix_het_alleles
from dnm_cohorts.de_novo import DeNovo

url = 'https://static-content.springer.com/esm/art%3A10.1038%2Fnature10989/MediaObjects/41586_2012_BFnature10989_MOESM11_ESM.xls'

def tidy_complex_alts(alts):
    """ sort out the "complex" allele events
    """
    alts = alts.copy()
    alts[60] = "S"
    alts[77] = "1D, -G"
    alts[115] = "1I, +C"
    alts[132] = "R"
    alts[184] = "1D, -G"
    
    return alts

async def fix_alleles(limiter, data):
    
    ref = data['ref'].copy()
    alt = data['alt'].copy()
    
    # fix the alleles and positions for insertions and deletions
    dels = alt.str.contains('D, *-')
    ins = alt.str.contains('I, *\+')
    
    # find the reference sequence at the site. Deletions use this as the
    # alternate allele, whereas the insertions use this as the reference allele
    seqs = {}
    dels_coords = [(x.chrom, x.pos, x.pos, x.build) for i, x in data[dels].iterrows()]
    ins_coords = [(x.chrom, x.pos, x.pos, x.build) for i, x in data[ins].iterrows()]
    async with trio.open_nursery() as nursery:
        for x in dels_coords + ins_coords:
            nursery.start_soon(parallel_sequence, limiter, *x[:3], seqs, x[3])
    
    # tidy up the deletion alleles
    dels_alt = [seqs[x] for x in dels_coords]
    ref[dels] = dels_alt + alt[dels].str.replace('\dD, *-', '', regex=True)
    alt[dels] = dels_alt
    
    # tidy up the insertion alleles
    ins_ref = [seqs[x] for x in ins_coords]
    ref[ins] = ins_ref
    alt[ins] = ins_ref + alt[ins].str.replace('\dI, *\+', '', regex=True)
    
    return ref, alt

async def oroak_nature_de_novos(result, limiter):
    """ get de novo data from the O'Roak et al autism exome study
    
    Supplementary table 3 from:
    O'Roak et al. (2012) Nature 485:246-250
    doi: 10.1038/nature10989
    
    Returns:
        data frame of de novos, with standardised genome coordinates and VEP
        consequences for each variant
    """
    logging.info('getting O\'Roak et al Nature 2012 de novos')
    data = pandas.read_excel(url, sheet_name="Supplementary Table 3",
        skipfooter=3, engine='xlrd')
    
    # standardise the chrom, position and allele column names
    data['chrom'] = data['Chromosome'].astype(str)
    data['pos'] = data['Position (hg19)'].astype(int)
    data['ref'] = data['Ref']
    data['alt'] = data['Allele']
    data['build'] = 'grch37'
    
    data['alt'] = tidy_complex_alts(data['alt'])
    data['ref'], data['alt'] = await fix_alleles(limiter, data)
    
    alleles = [ fix_het_alleles(x.ref, x.alt) for i, x in data.iterrows() ]
    data['ref'], data['alt'] = list(zip(*alleles))
    
    data['person_id'] = data['Person'] + '|asd_cohorts'
    data['study'] = '10.1038/nature10989'
    data['confidence'] = 'high'
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, row.build)
        vars.add(var)
    
    result.append(vars)
