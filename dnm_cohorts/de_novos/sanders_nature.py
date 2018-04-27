
import pandas

from dnm_cohorts.ensembl import cq_and_symbols, genome_sequence
from dnm_cohorts.fix_alleles import fix_het_alleles

url = 'http://www.nature.com/nature/journal/v485/n7397/extref/nature10945-s3.xls'

def fix_alleles(data):
    
    alt = data['alt'].copy()
    ref = data['ref'].copy()
    
    # get the correct ref and alt alleles for indels
    idx = alt.str.contains(':')
    delta = [ len(x.split(':')[1]) for x in alt[idx] ]
    
    alt[idx] = [ genome_sequence(x.chrom, x.pos, x.pos) for i, x in data[idx].iterrows() ]
    ref[idx] = [ genome_sequence(x.chrom, x.pos, x.pos + d) for (i, x), d in zip(data[idx].iterrows(), delta) ]
    
    return ref, alt

def sanders_nature():
    """ get de novo data from the Sanders et al autism exome study
    
    Supplementary table 2 (where the excel sheets for the probands and
    siblings have been combined) from:
    Sanders et al. (2012) Nature 485:237-241
    doi: 10.1038/nature10945
    
    Returns:
        data frame of de novos, with standardised genome coordinates and VEP
        consequences for each variant
    """
    
    probands = pandas.read_excel(url, sheet_name='Probands')
    siblings = pandas.read_excel(url, sheet_name='Siblings')
    data = probands.append(siblings, ignore_index=True)
    
    data['person_id'] = data['Child_ID']
    data['chrom'] = data['Chr'].str.replace('chr', '')
    data['pos'] = data['Pos (hg19)']
    data['ref'] = data['Ref']
    data['alt'] = data['Alt']
    
    # clean up the alleles
    data['ref'], data['alt'] = fix_alleles(data)
    alleles = [ fix_het_alleles(x.ref, x.alt) for i, x in data.iterrows() ]
    data['ref'], data['alt'] = list(zip(*alleles))
    
    cqs, symbols = cq_and_symbols(data.chrom, data.pos, data.ref, data.alt)
    data['consequence'] = cqs
    data['symbol'] = symbols
    
    data['study'] = "sanders_nature_2012"
    
    return data[['person_id','chrom', 'pos', 'ref', 'alt', 'symbol',
        'consequence', 'study']]
