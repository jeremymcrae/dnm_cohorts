
import re

from hgvs.parser import Parser
hgvs_parser = Parser()

from dnm_cohorts.ensembl import genome_sequence
from dnm_cohorts.fix_alleles import fix_substitution, fix_deletion, fix_insertion

def fix_hgvs_coordinates(coords):
    """ extract genomic coordinates for variants encoded as HGVS genomic
    
    Args:
        variants: data frame of variants
        column: name of column containing HGVS coordinate
    
    Returns:
        a data frame with chrom, pos, and allele columns.
    
    Examples:
    fix_hgvs_coordinates(['chr7:g.155556643G>A',
        'chr3:g.11060365_11060365del', 'chr13:g.50057690_50057691insA'])
    """
    
    chroms, positions, refs, alts = [], [], [], []
    for coord in coords:
        var = hgvs_parser.parse_hgvs_variant(coord)
        chrom = var.ac.replace('chr', '')
        pos = var.posedit.pos.start.base
        end = var.posedit.pos.end.base
        type = var.posedit.edit.type
        ref = var.posedit.edit.ref
        
        if type == 'del':
            ref = genome_sequence(chrom, pos, end + 1)
            alt = ref[0]
        elif type == 'delins':
            ref = genome_sequence(chrom, pos, end)
            alt = var.posedit.edit.alt
        elif type == 'ins':
            ref = genome_sequence(chrom, pos, end)
            alt = ref + var.posedit.edit.alt
        elif type == 'sub':
            alt = var.posedit.edit.alt
        elif type == 'dup':
            ref = genome_sequence(chrom, pos, end + 1)
            alt = ref + ref
        
        chroms.append(chrom)
        positions.append(pos)
        refs.append(ref)
        alts.append(alt)
    
    return chroms, positions, refs, alts

def fix_coordinates(coords, alleles):
    """
    fix_coordinates(["chr1:10000"], ["chr1:10000:A:G"])
    fix_coordinates(["chr1:10000"], ["chr1:10003:ATGC:G"])
    """
    
    chroms, positions, refs, alts = [], [], [], []
    for a, b in zip(coords, alleles):
        chrom, pos = a.split(':')
        _, _, ref, alt = b.split(':')
        chroms.append(chrom.upper().replace('CHR', ''))
        positions.append(int(pos))
        refs.append(ref)
        alts.append(alt)
    
    return chroms, positions, refs, alts

def fix_coordinates_with_allele(coords, alleles):
    """
    fix_coordinates_with_allele(["chr1:10000"], ["A/G"])
    fix_coordinates_with_allele(["chr1:10000", "chr2:20000"], ["A/G", "T/C"])
    fix_coordinates_with_allele(["chr1:10000"], ["ATGC/G"])
    fix_coordinates_with_allele(["chr1:10000"], ["sub(G-&gt;T)"])
    fix_coordinates_with_allele(["chr1:10000"], ["del(1)"])
    fix_coordinates_with_allele(["chr1:10000"], ["ins(ATG)"])
    """
    
    chroms, positions, refs, alts = [], [], [], []
    for coord, allele in zip(coords, alleles):
        chrom, start = coord.split(':')
        chrom = chrom.upper().replace('CHR', '')
        start = int(start)
        end = start
        
        if 'sub' in allele:
            ref, alt = fix_substitution(chrom, start, end, allele)
        elif 'del' in allele:
            ref, alt = fix_deletion(chrom, start, end, allele)
        elif 'ins' in allele:
            ref, alt = fix_insertion(chrom, start, end, allele)
        else:
            ref, alt = allele.split('/')
        
        chroms.append(chrom)
        positions.append(int(start))
        refs.append(ref)
        alts.append(alt)
    
    return chroms, positions, refs, alts
