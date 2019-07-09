
from itertools import groupby

consequences = ["transcript_ablation", "splice_donor_variant",
    "splice_acceptor_variant", "stop_gained", "frameshift_variant",
    "initiator_codon_variant", "stop_lost", "start_lost",
    "transcript_amplification", 'conserved_exon_terminus_variant',
    "inframe_insertion", "inframe_deletion", "missense_variant",
    "protein_altering_variant", "splice_region_variant",
    "incomplete_terminal_codon_variant", "stop_retained_variant",
    "synonymous_variant", "coding_sequence_variant", "mature_miRNA_variant",
    "5_prime_UTR_variant", "3_prime_UTR_variant", "non_coding_exon_variant",
    "non_coding_transcript_exon_variant", "intron_variant",
    "NMD_transcript_variant", "non_coding_transcript_variant",
    "nc_transcript_variant", "upstream_gene_variant", "downstream_gene_variant",
    "TFBS_ablation", "TFBS_amplification", "TF_binding_site_variant",
    "regulatory_region_ablation", "regulatory_region_amplification",
    "regulatory_region_variant", "feature_elongation", "feature_truncation",
    "intergenic_variant"]
severity = dict(zip(consequences, range(len(consequences))))

def drop_inperson_duplicates(de_novos):
    """ get independent mutation events per person
    
    Occasionally an individual will have multiple de novo mutations within a
    gene. We only want to count the mutated gene once per individual, while
    preferring to count the most damaging mutations.
    
    Args:
        list of DeNovo objects
    """
    # make sure the dataset is sorted, this will sort by person ID then chrom
    # and pos, so all the variants in a single gene will be grouped
    de_novos = sorted(de_novos)
    
    included = []
    for (_, symbol), group in groupby(de_novos, key=lambda x: (x.person_id, x.symbol)):
        group = list(group)
        if symbol != '' and symbol is not None:
            cq = min(( x.consequence for x in group ), key=lambda x: severity[x])
            group = [ x for x in group if x.consequence == cq ]
            group = group[:1]
        included += group
    
    return included
