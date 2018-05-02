
import pandas

from dnm_cohorts.ensembl import genome_sequence
from dnm_cohorts.fix_alleles import fix_het_alleles
from dnm_cohorts.de_novo import DeNovo

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

def sanders_nature_de_novos():
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
    
    data['person_id'] = data['Child_ID'].astype(str)
    data['chrom'] = data['Chr'].str.replace('chr', '')
    data['pos'] = data['Pos (hg19)']
    data['ref'] = data['Ref']
    data['alt'] = data['Alt']
    
    # clean up the alleles
    data['ref'], data['alt'] = fix_alleles(data)
    alleles = [ fix_het_alleles(x.ref, x.alt) for i, x in data.iterrows() ]
    data['ref'], data['alt'] = list(zip(*alleles))
    
    data['person_id'] += "|asd_cohorts"
    data['study'] = "10.1038/nature10945"
    data['confidence'] = 'high'
    
    vars = set()
    for i, row in data.iterrows():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence)
        vars.add(var)
    
    return vars
