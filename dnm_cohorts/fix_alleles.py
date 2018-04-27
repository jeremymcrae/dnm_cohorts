# functions to standardise allele codes into ref/alt format as nonambiguous
# IUPAC bases

import re

from dnm_cohorts.ensembl import genome_sequence

def fix_substitution(chrom, start, end, alleles):
    """fix substitution allele codes
    
    fix the allele column for variants with allele columns that are structured
    like "sub(G-&gt;T)" (the "-&gt;" translates to ">", and sub(G->T), this is
    an excel to R conversion issue. Perhaps it is unicode from excel?
    
    Args:
        variants data frame of variants
        allele_column name of column containing allele information
    
    Returns:
        a data frame with start_pos, end_pos and allele columns.
    """
    
    pat = re.compile('\(|\)|sub')
    alleles = pat.sub('', alleles)
    
    sep = re.compile('-[&gt;|>]*')
    return sep.split(alleles)

def fix_deletion(chrom, start, end, allele):
    """ fix deletion allele codes
    
    fix the allele column for variants with allele columns that are structured
    like "del(1)"
    
    Args:
        variants: data frame of variants
        allele_column: name of column containing allele information
    
    Returns:
        a data frame with start_pos, end_pos and allele columns.
    """
    
    pat = re.compile('\(|\)|del')
    distance = int(pat.sub('', allele))
    
    alt = genome_sequence(chrom, start, end)
    ref = genome_sequence(chrom, start, end + distance)
    
    return ref, alt

def fix_insertion(chrom, start, end, allele):
    """ fix insertion allele codes
    
    fix the allele column for variants with allele columns that are structured
    like "ins(1)"
    
    Args:
        variants data frame of variants
        allele_column name of column containing allele information
    
    Returns:
        a data frame with start_pos, end_pos and allele columns.
    """
    
    pat = re.compile('\(|\)|ins')
    insert = pat.sub('', allele)
    
    ref = genome_sequence(chrom, start - 1, end - 1)
    alt = ref + insert
    
    return ref, alt


def fix_duplication(chrom, start, end, allele):
    """ fix duplication allele codes
    
    fix the allele column for variants with allele columns that are structured
    like "dup"
    
    Args:
        variants data frame of variants
        allele_column name of column containing allele information
    
    Returns:
        a data frame with start_pos, end_pos and allele columns.
    """
    
    ref = genome_sequence(chrom, start - 1, end - 1)
    alt = ref * 2
    
    return start, ref, alt

class HetFixer:
    """ correct alt alleles which have been encoded as an IUPAC ambiguous base
    
    Sometimes the de novo variants from studies provide alt alleles as "R", or
    "Y", which indicate ambigous bases. We can identify the correct alt base by
    comparison with the reference allele.
    """
    IUPAC = {"R": set(["A", "G"]), "Y": set(["C", "T"]), "S": set(["G", "C"]),
             "W": set(["A", "T"]), "K": set(["G", "T"]), "M": set(["A", "C"])}
    
    def __call__(self, ref, alt):
        # figure the correct base from the ambigous base which is not the
        # reference allele.
        if alt in self.IUPAC:
            alt = set(self.IUPAC[alt]) - set([ref])
            alt = list(alt)[0]
        
        return ref, alt

fix_het_alleles = HetFixer()
