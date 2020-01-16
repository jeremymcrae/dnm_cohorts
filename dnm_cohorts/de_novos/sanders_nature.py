
import trio
import logging

import pandas

from dnm_cohorts.ensembl import parallel_sequence
from dnm_cohorts.fix_alleles import fix_het_alleles
from dnm_cohorts.de_novo import DeNovo

url = 'http://www.nature.com/nature/journal/v485/n7397/extref/nature10945-s3.xls'

async def fix_alleles(limiter, data):
    
    alt = data['alt'].copy()
    ref = data['ref'].copy()
    
    idx = alt.str.contains(':')
    
    seqs = {}
    alts_coords = [(x.chrom, x.pos, x.pos, x.build) for i, x in data[idx].iterrows()]
    refs_coords = [(x.chrom, x.pos, x.pos + len(x.alt.split(':')[1]), x.build) for i, x in data[idx].iterrows()]
    async with trio.open_nursery() as nursery:
        for x in alts_coords + refs_coords:
            nursery.start_soon(parallel_sequence, limiter, *x[:3], seqs, x[3])
    
    alt[idx] = [seqs[x] for x in alts_coords]
    ref[idx] = [seqs[x] for x in refs_coords]
    
    return list(ref), list(alt)

async def sanders_nature_de_novos(result, limiter):
    """ get de novo data from the Sanders et al autism exome study
    
    Supplementary table 2 (where the excel sheets for the probands and
    siblings have been combined) from:
    Sanders et al. (2012) Nature 485:237-241
    doi: 10.1038/nature10945
    
    Returns:
        data frame of de novos, with standardised genome coordinates and VEP
        consequences for each variant
    """
    logging.info('getting Sanders et al Nature 2012 de novos')
    probands = pandas.read_excel(url, sheet_name='Probands', engine='xlrd')
    siblings = pandas.read_excel(url, sheet_name='Siblings', engine='xlrd')
    data = probands.append(siblings, ignore_index=True)
    
    data['person_id'] = data['Child_ID'].astype(str)
    data['chrom'] = data['Chr'].str.replace('chr', '')
    data['pos'] = data['Pos (hg19)']
    data['ref'] = data['Ref']
    data['alt'] = data['Alt']
    data['build'] = 'grch37'
    
    # clean up the alleles
    data['ref'], data['alt'] = await fix_alleles(limiter, data)
    alleles = [ fix_het_alleles(x.ref, x.alt) for i, x in data.iterrows() ]
    data['ref'], data['alt'] = list(zip(*alleles))
    
    data['person_id'] += "|asd_cohorts"
    data['study'] = "10.1038/nature10945"
    data['confidence'] = 'high'
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, row.build)
        vars.add(var)
    
    result.append(vars)
