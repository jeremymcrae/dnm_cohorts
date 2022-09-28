
from itertools import groupby

from dnm_cohorts.ensembl import severity

def drop_inperson_duplicates(de_novos):
    """ get independent mutation events per person
    
    Occasionally an individual will have multiple de novo mutations within a
    gene. We only want to count the mutated gene once per individual, while
    preferring to count the most damaging mutations.
    
    Args:
        list of DeNovo objects
    """
    # make sure the dataset is sorted by person ID and symbol, so we can group
    # consecutive variants in the same person and gene
    de_novos = sorted(de_novos, key=lambda x: (x.person_id, x.symbol))
    
    included = []
    for (_, symbol), group in groupby(de_novos, key=lambda x: (x.person_id, x.symbol)):
        group = list(group)
        if symbol != '' and symbol is not None:
            cq = min(( x.consequence for x in group ), key=lambda x: severity[x])
            group = [ x for x in group if x.consequence == cq ]
            group = group[:1]
        included += group
    
    return included
