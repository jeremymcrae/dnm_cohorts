import logging
from itertools import groupby

import pandas
from liftover import get_lifter

from dnm_cohorts.person import Person

url = 'https://static-content.springer.com/esm/art%3A10.1038%2Fs41588-022-01104-0/MediaObjects/41588_2022_1104_MOESM3_ESM.xlsx'

def clean_ssc_ids(df):
    ''' lean sample IDs from the SSC subset, for consistency with previous IDs.
    
    I spot checked one sample via the family ID and confirmed the de novos in
    this dataframe were present (along with others from WGS calling, which is
    why I'm not simply setting this study as the source of truth).
    '''
    in_ssc = df['Cohort'] == 'SSC'
    control = df['Affected_Status'] == 1
    sample_id = df['person_id']
    sample_id.loc[in_ssc] = df['Family'][in_ssc].astype('str')
    sample_id.loc[in_ssc & control] = sample_id.loc[in_ssc & control] + '.s1'
    sample_id.loc[in_ssc & ~control] = sample_id.loc[in_ssc & ~control] + '.p1'
    sample_id.loc[in_ssc] = sample_id.loc[in_ssc] + '|asd_cohorts'
    return sample_id

def open_fu_nature_genetics_cohort():
    """ gets individual level data for Fu et al ASC Consortium
    
    Supplementary Table 4 from:
    Fu et al. Nature Genetics 2022, doi: 10.1038/s41588-022-01104-0
    
    Zhou et al, Nature Genetics doi:10.1038/s41588-022-01148-2 published an 
    overlapping dataset the same day as this dataset. The two publications are
    from two different consortia 
        - Fu et al for the ASC Consortium
        - Zhou et al from the SPARK consortium
    
    Each consortium contributed 6-7k ASD trios, and presumably they both published
    on the joint dataset. I skipped Zhou et al, because their supplemental tables
    omit a table of every individual in the dataset, only showing individuals
    with de novo mutations.
    
    Zhou et al uses hg19, Fu et al uses grch38, my preference is for grch38. Zhou 
    et al includes chrX variants, so I might have to include those.
    
    I checked the overlap, and about 2/3 of the variants have exact matches by 
    coordinate. Of the variants unique to each dataset, they are fairly similar:
        missense to synonymous ratios:
            matched:     2.587
            Fu unique:   2.560
            Zhou unique: 2.475
        Fraction in high pLI gene:
            matched:     0.275
            Fu unique:   0.266
            Zhou unique: 0.240
    
    The Fu unique high pLI fraction seems smaller, but there are more Fu unique
    variants (14539) than Zhou unique variants (10066), so the number in high pLI
    genes is much higher in Fu unique.
    
    These numbers can be verified with: dnm_cohorts.de_novos.fu_nature_genetics.check_fu_vs_zhou()
    """
    logging.info('getting Fu et al Nature Genetics 2022 cohort')
    data = pandas.read_excel(url, 'Supplementary Table 4', skipfooter=14)
    data['person_id'] = data['Sample'].astype(str) + '|asd_cohorts'
    data['sex'] = data['Sex'].str.lower()
    control = data['Affected_Status'] == 1
    data['status'] = 'HP:0000717'
    data.loc[control, 'status'] = 'unaffected'
    data['person_id'] = clean_ssc_ids(data)
    
    study = ['10.1038/s41588-022-01104-0']
    
    persons = set()
    for row in data.itertuples():
        person = Person(row.person_id, row.sex, [row.status], study)
        person.family = row.Family
        
        persons.add(person)
        
        # FIXME I found a duplicate de novo call in the table for 12603.p1|asd_cohorts
        # FIXME at 12:31667984 G->A. there are two rows for this variant, each 
        # FIXME for a different gene symbol (METTL20 and ETFBKMT), which come
        # FIXME from two different studies - 10.1126/science.aat6576 and 
        # FIXME 10.1038/nature10989. Figure out why this occurs, and prevent it 
        # FIXME and others.
        
        # FIXME There are some large families of sequenced sibs in this cohort,
        # FIXME e.g family ID SF0094948. We should drop to a single affected 
        # FIXME proband to avoid potential confounders from recurrent mutations 
        # FIXME in the germline.
    
    return persons


TRANSDICT = str.maketrans('ACGTacgt', 'TGCAtgca')
def revcomp(seq):
    ''' reverse complement a sequence
    '''
    return seq.translate(TRANSDICT)[::-1]

def to_build(lifter, row):
    ''' lift variant to a different genome build
    '''
    try:
        coords = lifter[row.chrom][row.pos - 1]
    except KeyError:
        logging.warning(f'cannot lift: {row.chrom}:{row.pos} {row.ref}->{row.alt}')
        return ('', 0, '', '')
    
    if not coords:
        logging.warning(f'cannot lift: {row.chrom}:{row.pos} {row.ref}->{row.alt}')
        return ('', 0, '', '')
    
    # NOTE: This doesn't account for left-aligning indels, or where the
    # NOTE: ref is now the alt. I'm also not rechecking the symbol and
    # NOTE: consequence annotations.
    assert len(coords) == 1
    chrom, pos, strand = coords[0]
    pos += 1
    ref, alt = row.ref, row.alt
    if strand == '-':
        ref = revcomp(row.ref)
        alt = revcomp(row.alt)
    
    return chrom, pos, ref, alt

def open_fu_dnms():
    ''' open Fu et al variants
    '''
    df = pandas.read_excel('https://static-content.springer.com/esm/' \
        'art%3A10.1038%2Fs41588-022-01104-0/MediaObjects/'\
        '41588_2022_1104_MOESM3_ESM.xlsx', 'Supplementary Table 20', skipfooter=18)
    # make coord column names consistent
    df[['chrom', 'pos', 'ref', 'alt']] = df['Variant'].str.split(':', expand=True)
    df['pos'] = df['pos'].astype(int)
    df['symbol'] = df['gene']
    df['consequence'] = df['Simplified_csq']
    
    df['varid'] = list(zip(df['chrom'], df['pos'], df['ref'], df['alt']))
    return df

def open_zhou_dnms():
    ''' open Zhou et al variants
    '''
    df = pandas.read_excel('https://static-content.springer.com/esm/' \
        'art%3A10.1038%2Fs41588-022-01148-2/MediaObjects/' \
        '41588_2022_1148_MOESM5_ESM.xlsx', 'SupplementaryData1_ASD_Discov_D', skipfooter=18)
    
    df = df.rename(columns={'Chrom': 'chrom', 'Position': 'pos', 'Ref': 'ref', 'Alt': 'alt'})
    df['chrom'] = df['chrom'].astype('str')
    df['symbol'] = df['HGNC']
    df['consequence'] = df['GeneEff']
    
    # lift Zhou variants to hg38
    lifter = get_lifter('hg19', 'hg38')
    lifted = [to_build(lifter, x) for x in df[['chrom', 'pos', 'ref', 'alt']].itertuples()]
    chrom, pos, ref, alt = list(zip(*lifted))
    df['chrom'] = [x[3:] for x in chrom]
    df['pos'] = pos
    df['ref'] = ref
    df['alt'] = alt
    
    df['varid'] = list(zip(df['chrom'], df['pos'], df['ref'], df['alt']))
    return df

def check_nearby(fu, zhou, fu_unique):
    ''' find variants without exact matches but with nearby matches instead
    '''
    nearby = 0
    i = 0
    for chrom, group in groupby(sorted(fu_unique), key=lambda x: x[0]):
        chr_matches = zhou.chrom == chrom
        positions = zhou['pos'][chr_matches].values
        ids = zhou.IID[chr_matches].values
        for chrom, pos, ref, alt in group:
            deltas = abs(positions - pos)
            idx = deltas.argmin()
            delta = deltas[idx]
            nearest = positions[idx]
            if delta < 10:
                fu_row = fu[fu['varid'] == (chrom, pos, ref, alt)].head(1).squeeze()
                if fu_row['Sample'] != ids[idx]:
                    continue
                nearby += 1
                match = zhou[chr_matches].iloc[idx]
                print(delta, chrom, pos, ref, alt, match.chrom, match.pos, match.ref, match.alt)
            i += 1
            if i % 1000 == 0:
                print(i, nearby, nearby / i)
    
    # this is a very small fraction, only 0.0039 (0.4%) of the Fu unique variants
    print(nearby, nearby / len(fu_unique))

def get_high_pli_genes(threshold=0.9):
    ''' load high pLI genes
    '''
    url = 'https://storage.googleapis.com/gcp-public-data--gnomad/release/2.1.1/' \
        'constraint/gnomad.v2.1.1.lof_metrics.by_gene.txt.bgz'
    pli = pandas.read_table(url, compression='gzip', sep='\t')
    return set(pli.gene[pli.pLI > threshold])

def check_dataset(rows, high_pli):
    ''' get the missense: synonymous ratio, and the fraction in high pLI genes
    '''
    n_missense = (rows.consequence.str.contains('missense')).sum()
    n_synonymous = (rows.consequence.str.contains('synonymous')).sum()
    mis_syn_ratio = n_missense / n_synonymous
    pli_fraction = rows.symbol.isin(high_pli).sum() / len(rows)
    return {'mis_syn': mis_syn_ratio, 'pli_ratio': pli_fraction}

def snv_fraction(coords):
    ''' check the fraction of coordinates which are for SNVs
    '''
    return sum(len(x[2]) == len(x[3]) for x in coords) / len(coords)

def check_fu_vs_zhou():
    fu = open_fu_dnms()
    zhou = open_zhou_dnms()
    
    fu_ids = set(fu['varid'])
    zhou_ids = set(zhou['varid'])
    
    matches = fu_ids & zhou_ids  # 2/3 have exact matches
    fu_unique = fu_ids - zhou_ids
    zhou_unique = zhou_ids - fu_ids
    
    print('matched SNV fraction:', snv_fraction(matches))
    print('fu_unique SNV fraction:', snv_fraction(fu_unique))
    print('zhou_unique SNV fraction:', snv_fraction([x for x in zhou_unique if x[0] != 'X']))
    
    #only a small fraction of the discrepant are due to chrX calls in zhou et al
    sum(x[0] == 'X' for x in zhou_unique) / len(zhou_unique)  
    
    check_nearby(fu, zhou, fu_unique)
    
    # potential checks for which dataset is better quality
    # of the unique variants, what's the missense/synonymous ratio
    # what proportion occur in high pLI genes
    pli_genes = get_high_pli_genes()
    matched_rows = zhou[zhou.varid.isin(matches) & (zhou.chrom != 'X')]
    zhou_rows = zhou[zhou.varid.isin(zhou_unique) & (zhou.chrom != 'X')]
    fu_rows = fu[fu.varid.isin(fu_unique)]
    print('matched:', check_dataset(matched_rows, pli_genes))
    print('zhou_unique:', check_dataset(zhou_rows, pli_genes))
    print('fu_unique:', check_dataset(fu_rows, pli_genes))
