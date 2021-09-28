
import logging

import trio
from intervaltree import IntervalTree

from dnm_cohorts.de_novos.jonsson_nature import jonsson_nature_de_novos
from dnm_cohorts.de_novos.halldorsson_science import halldorsson_science_de_novos

async def _get_cohorts():
    ''' get variants from Jonsson et al and Halldorsson et al only
    '''
    variants = []
    async with trio.open_nursery() as nursery:
        nursery.start_soon(jonsson_nature_de_novos, variants)
        nursery.start_soon(halldorsson_science_de_novos, variants)
    return variants

def to_intervaltree(de_novos):
    ''' convert list of de novos in a cohort to intervaltree, for easy indexing
    '''
    tree = {}
    for x in de_novos:
        if x.chrom not in tree:
            tree[x.chrom] = IntervalTree()
        tree[x.chrom].addi(x.pos, x.pos + 1, x.person_id)
    return tree

def by_sample_id(de_novos):
    ''' collect de novos by sample for a cohort
    '''
    samples = {}
    for x in de_novos:
        if x.person_id not in samples:
            samples[x.person_id] = []
        samples[x.person_id].append(x)
    return samples

def count_sample_matches(first, second):
    ''' count variant matches between samples from two different cohorts

    Args:
        first: list of variants for sample from one study
        second: list of variants from second study

    Returns:
        number of exact matches, and proportion of all variants that matched
    '''
    first = set((x.chrom, x.pos, x.ref, x.alt) for x in first if x.chrom != 'X')
    second = set((x.chrom, x.pos, x.ref, x.alt) for x in second  if x.chrom != 'X')

    intersect = len(first & second)
    union = len(first | second)

    return intersect, intersect / union

def find_jonsson_to_halldorsson_ids(jonsson, halldorsson):
    ''' find which samples from Jonsson et al are in Haldorsson et al

    The Jonsson et al and Haldorsson et al papers were from the same research 
    group, but published at different times, where Jonsson et al had 1323 
    samples with de novos and Haldorsson et al had 2976 samples with de novos.
    The assumption is Haldorsson et al is an expanded cohort building on Jonsson 
    et al. Unfortuantely, the sample ID schemes of the two cohorts do not match, 
    so we cannot match by given sample IDs. But the cohorts provide de novos 
    identified from WGS, and the chance of two samples having the same de novo 
    call is very low, so we can simple look for pairs of samples with a high 
    fraction of matching de novo calls.

    This found 1313 of the 1323 (99.2%) Jonsson samples have good matches in 
    Halldorsson et al. The proportion of de novo call matches between sample 
    replicates was fairly low, so the missing 10 might also occur in Halldorsson,
    but without matching calls between replicates. This effectively demonstrates
    that Jonsson et al has been superceded by Halldorsson et al.

    Args:
        jonsson: list of DeNovos for Jonsson et al
        halldorsson: list of DeNovos for Halldorsson et al

    Returns:
        dict mapping Jonsson sample ID to Halldorsson sample ID
    '''
    # index halldorsson by chrom and position, to quickly get variant matches
    halldorsson_tree = to_intervaltree(halldorsson)

    # group variants by sample
    jonsson_samples = by_sample_id(jonsson)
    halldorsson_samples = by_sample_id(halldorsson)

    sample_map = {}
    for sample in jonsson_samples:
        has_match = False
        for var in jonsson_samples[sample]:
            if has_match:
                break
            if var.chrom == 'X':
                continue

            matches = halldorsson_tree[var.chrom][var.pos]
            if len(matches) != 1:
                continue

            match = next(iter(matches)).data
            count, fraction = count_sample_matches(jonsson_samples[sample], halldorsson_samples[match])
            has_match = count >= 5 and fraction > 0.4
            if has_match:
                sample_map[sample] = match
    
    pct = (len(sample_map) / len(jonsson_samples)) * 100
    logging.info(f'{len(sample_map)} of the {len(jonsson_samples)} ({pct:.3g}%) Jonsson samples exist in Halldorsson et al.')

    return sample_map

def main():
    variants = trio.run(_get_cohorts)

    first = variants[0]
    if next(iter(first)).study == '10.1126/science.aau1043':
        halldorsson, jonsson = variants
    else:
        jonsson, halldorsson = variants

    mapped_ids = find_jonsson_to_halldorsson_ids(jonsson, halldorsson)
    
    print('jonsson_id\thalldorsson_id')
    for k, v in mapped_ids.items():
        print(f'{k}\t{v}')

if __name__ == '__main__':
    main()
