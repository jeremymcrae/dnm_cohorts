
import logging

import pandas

from dnm_cohorts.ensembl import genome_sequence
from dnm_cohorts.fix_alleles import fix_het_alleles
from dnm_cohorts.de_novo import DeNovo

url = 'http://www.nature.com/nature/journal/v485/n7397/extref/nature10945-s3.xls'

async def fix_alleles(limiter, data):
    
    alt = list(data['alt'])
    ref = list(data['ref'])
    
    for i, (chrom, pos, a, r) in enumerate(zip(data.chrom, data.pos, alt, ref)):
        if not ':' in a:
            continue
        alt[i] = await genome_sequence(limiter, chrom, pos, pos)
        ref[i] = await genome_sequence(limiter, chrom, pos, pos + len(a.split(':')[1]))
    
    return ref, alt

async def sanders_nature_de_novos(limiter):
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
    probands = pandas.read_excel(url, sheet_name='Probands')
    siblings = pandas.read_excel(url, sheet_name='Siblings')
    data = probands.append(siblings, ignore_index=True)
    
    data['person_id'] = data['Child_ID'].astype(str)
    data['chrom'] = data['Chr'].str.replace('chr', '')
    data['pos'] = data['Pos (hg19)']
    data['ref'] = data['Ref']
    data['alt'] = data['Alt']
    
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
            row.study, row.confidence, 'grch37')
        vars.add(var)
    
    return vars
