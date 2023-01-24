
import logging

import pandas

from dnm_cohorts.de_novo import DeNovo
from dnm_cohorts.cohorts.fu_nature_genetics import clean_ssc_ids

fu_url = 'https://static-content.springer.com/esm/art%3A10.1038%2Fs41588-022-01104-0/MediaObjects/41588_2022_1104_MOESM3_ESM.xlsx'
zhou_url = 'https://static-content.springer.com/esm/art%3A10.1038%2Fs41588-022-01148-2/MediaObjects/41588_2022_1148_MOESM5_ESM.xlsx'

async def fu_nature_genetics_de_novos(result):
    """ gets individual level data for Fu et al
    
    Supplementary Table 20 from:
    Fu et al. Nature Genetics 2022, doi: 10.1038/s41588-022-01104-0
    """
    logging.info('getting Fu et al Nature Genetics 2022 de novos')
    data = pandas.read_excel(fu_url, 'Supplementary Table 20', skipfooter=18)
    
    sample_df = pandas.read_excel(fu_url, 'Supplementary Table 4', skipfooter=14)
    sample_df['person_id'] = sample_df['Sample'].astype(str) + '|asd_cohorts'
    sample_df['person_id'] = clean_ssc_ids(sample_df)
    
    data['person_id'] = data['Sample'].map(dict(zip(sample_df.Sample, sample_df.person_id)))
    
    data[['chrom', 'pos', 'ref', 'alt']] = data['Variant'].str.split(':', expand=True)
    data['pos'] = data['pos'].astype(int)
    data['study'] = '10.1038/s41588-022-01104-0'
    data['confidence'] = 'high'
    
    variants = set()
    for row in data.itertuples():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, 'grch38')
        variants.add(var)
    
    result.append(variants)

async def open_zhou_de_novos(url):
    ''' reconcile de novo tables between Zhou et al and Fu et al
     
    Zhou et al (Nature Genetics 54:1305-1319) and Fu et al (Nature Genetics 54:1320-1331)
    published in the same issue on largely overlapping datasets. Zhou et al was
    from the SPARK consortium, and Fu et al was from the ASC (or SSC?) consortium.
    
    Fu et al listed all samples in their cohort, which is why I'm using theirs, 
    but they didn't report chrX de novos. Fortunately, those were rported in 
    Zhou et al, so we can pull them from there. We need to do a little work to
    reconcile sample IDs and absence of a few samples from Fu et al. 
    '''
    df = pandas.read_excel(url, 'SupplementaryData1_ASD_Discov_D', skipfooter=18)
    df = df.rename(columns={'Chrom': 'chrom', 'Position': 'pos', 'Ref': 'ref', 
                            'Alt': 'alt', 'IID': 'person_id', 'Cohort': 'cohort'})
    df['person_id'] = df['person_id'].astype('str')
    df['chrom'] = df['chrom'].astype('str')
    df['symbol'] = df['HGNC']
    df['consequence'] = df['GeneEff']
    
    # fix some sample IDs with discrepant IDs
    idx = df['person_id'].str.startswith('CC')
    df.loc[idx, 'person_id'] = df.loc[idx, 'person_id'].str.replace('.', '_')
    
    # fix other sample IDs with discrepant IDs
    idx = df['person_id'].str.contains('@', regex=False)
    df.loc[idx, 'person_id'] = df.loc[idx, 'person_id'].str.replace('@', '_')
    
    return df

def find_missing_zhou_samples(zhou, fu_sample_df):
    
    # the zhou cohort includes samples from four cohorts - ASC, SPARK, MSSNG and SSC
    # All but a  few SPARK samples are in the Fu dataset, and the MSSNG samples are
    # from Yuen et al, so those are captured elsewhere
    pandas.crosstab(zhou['cohort'], zhou['matched'], values=zhou['person_id'], aggfunc=lambda x: len(x.unique()))
    # >>> matched  False  True
    # >>> ASC         42  3074
    # >>> MSSNG     2645     8
    # >>> SPARK       44  7357
    # >>> SSC        420  3188

    # I checked the 8 MSSNG samples in Fu et al, and all have IDs like AUXXXXXXX e.g.
    zhou[(zhou['cohort'] == 'MSSNG') & zhou['matched']]
    # >>> cohort  person_id
    # >>>  MSSNG  AU3692301
    # >>>  MSSNG  AU1635302

    # The AUXXXXXXX samples in Fu et al are all from one substudy: ASC_B14. I think
    # I'm ok ignoring that small overlap.
    fu_sample_df[fu_sample_df.person_id.str.startswith('AU') & 
            (fu_sample_df.person_id.str.len() == 9)].VCF_batch.value_counts()

    # I'll have to exclude importing from the 17 missing SPARK samples
    spark_missing = zhou['person_id'][(zhou['cohort'] == 'SPARK') & ~zhou['matched']]

    # of the missing 42 ASC samples (vs 3074 found), most sample IDs are found in
    # other, earlier studies, so I can exclude those.
    asc_missing = set(zhou['person_id'][(zhou['cohort'] == 'ASC') & ~zhou['matched']])

    # the missing 420 SSC samples are from Sanders et al Neuron 2015 87:1215-1233.
    # At least, the ones I spot checked were, so these are included already.
    ssc_missing = set(zhou['person_id'][(zhou['cohort'] == 'SSC') & ~zhou['matched']])
    
    return spark_missing | asc_missing | ssc_missing
