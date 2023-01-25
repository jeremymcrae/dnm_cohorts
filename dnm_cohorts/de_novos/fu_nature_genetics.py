
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
    sample_df = sample_df.rename(columns={'Cohort': 'cohort'})
    sample_df['person_id'] = sample_df['Sample'].astype(str) + '|asd_cohorts'
    sample_df['person_id'] = clean_ssc_ids(sample_df)
    
    data['person_id'] = data['Sample'].map(dict(zip(sample_df.Sample, sample_df.person_id)))
    
    data[['chrom', 'pos', 'ref', 'alt']] = data['Variant'].str.split(':', expand=True)
    data['pos'] = data['pos'].astype(int)
    data['study'] = '10.1038/s41588-022-01104-0'
    data['confidence'] = 'high'
    data['build'] = 'grch38'
    
    variants = set()
    for row in data.itertuples():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, row.build)
        variants.add(var)
    
    # fill in the missing chrX de novos from Zhou et al dataset
    zhou = await import_zhou_chrX_calls(sample_df)
    for row in zhou.itertuples():
        var = DeNovo(row.person_id, row.chrom, row.pos, row.ref, row.alt,
            row.study, row.confidence, row.build)
        variants.add(var)
    
    result.append(variants)

async def import_zhou_chrX_calls(fu_sample_df):
    ''' import chrX de novo calls from Zhou et al to fill in the Fu et al dataset
    '''
    zhou = await open_zhou_de_novos(zhou_url)
    zhou_missing = find_missing_zhou_samples(zhou, fu_sample_df)
    zhou = zhou[~zhou['person_id'].isin(zhou_missing)]
    return zhou[zhou['chrom'] == 'X']

async def open_zhou_de_novos(url):
    ''' reconcile de novo tables between Zhou et al and Fu et al
     
    Zhou et al (Nature Genetics 54:1305-1319) and Fu et al (Nature Genetics 54:1320-1331)
    published in the same issue on largely overlapping datasets. Zhou et al was
    from the SPARK consortium, and Fu et al was from the ASC (or SSC?) consortium.
    
    Fu et al listed all samples in their cohort, which is why I'm using theirs, 
    but they didn't report chrX de novos. Fortunately, those were reported in 
    Zhou et al, so we can pull them from there. We need to do a little work to
    reconcile sample IDs and absence of a few samples from Fu et al. 
    '''
    df = pandas.read_excel(url, 'SupplementaryData1_ASD_Discov_D', skipfooter=18)
    df = df.rename(columns={'Chrom': 'chrom', 'Position': 'pos', 'Ref': 'ref', 
                            'Alt': 'alt', 'IID': 'person_id', 'Cohort': 'cohort'})
    df['person_id'] = df['person_id'].astype('str') + '|asd_cohorts'
    df['chrom'] = df['chrom'].astype('str')
    df['symbol'] = df['HGNC']
    df['consequence'] = df['GeneEff']
    df['study'] = '10.1038/s41588-022-01148-2'
    df['build'] = 'grch37'
    
    # fix some sample IDs with discrepant IDs
    idx = df['person_id'].str.startswith('CC')
    df.loc[idx, 'person_id'] = df.loc[idx, 'person_id'].str.replace('.', '_', regex=False)
    
    # fix other sample IDs with discrepant IDs
    idx = df['person_id'].str.contains('@', regex=False)
    df.loc[idx, 'person_id'] = df.loc[idx, 'person_id'].str.replace('@', '_', regex=False)
    
    return df

def find_missing_zhou_samples(zhou, fu_sample_df):
    ''' identify samples in Zhou et al that are missing from Fu et al.
    
    We need to avoid including a few samples from Zhou et al that are not present 
    in Fu et al, since we are taking Fu et al as our source of truth for all but
    chrX de novos.
    '''
    # identify the samples in Zhou et al which are also in Fu et al.
    zhou['matched'] = zhou['person_id'].isin(fu_sample_df['person_id'])
    
    # the Zhou cohort includes samples from four cohorts - ASC, SPARK, MSSNG and SSC
    # All but a few SPARK samples are in the Fu dataset, and the MSSNG samples are
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
    spark_missing = set(zhou['person_id'][(zhou['cohort'] == 'SPARK') & ~zhou['matched']])

    # of the missing 42 ASC samples (vs 3074 found), most sample IDs are found in
    # other, earlier studies, so I can exclude those.
    asc_missing = set(zhou['person_id'][(zhou['cohort'] == 'ASC') & ~zhou['matched']])

    # the missing 420 SSC samples are from Sanders et al Neuron 2015 87:1215-1233.
    # At least, the ones I spot checked were, so these are included already.
    ssc_missing = set(zhou['person_id'][(zhou['cohort'] == 'SSC') & ~zhou['matched']])
    
    return spark_missing | asc_missing | ssc_missing

def all_cohort_matches(df: pandas.DataFrame, sample_id: str):
    ''' find all rows in the combined cohort for a given sample ID
    
    Args:
        df: pandas Dataframe with person_id column
        sample_id: sample_id of sample to check
    
    Returns:
        rows matching the sample ID
    '''
    return df[df.person_id.str == sample_id ]

def in_multiple_studies(df: pandas.DataFrame, sample_id: str):
    ''' check if a sample was reported in multiple studies
    
    Args:
        df: pandas Dataframe with person_id column
        sample_id: sample_id of sample to check
    
    Returns:
        true/false for whether the sample is in multjple studies
    '''
    rows = all_cohort_matches(df, sample_id)
    if len(rows) > 1:
        raise ValueError(f'too many sample matches for {sample_id}: {sorted(set(rows.person_id))}')
    elif len(rows) == 0:
        raise ValueError(f'no rows found for {sample_id}')
    return len(rows.squeeze().studies.split(',')) > 1

def categorize_missing_fu_samples(fu_cohort, fu, zhou):
    ''' find samples in Fu et al which are missing from Zhou et al
    '''
    # get a table with sample IDs from all de novo studies, so we can check if 
    # samples were reported previously
    full_cohort_url = 'https://github.com/jeremymcrae/dnm_cohorts/raw/1.6.0/dnm_cohorts/data/cohort.txt.gz'
    cohort = pandas.read_table(full_cohort_url)
    
    # identify the samples in Fu et al which are also in Zhou et al.
    fu_cohort['matched'] = fu_cohort['person_id'].isin(zhou['person_id'])
    
    # find the missing samples by origin (vcf_batch)
    pandas.crosstab(fu_cohort['vcf_batch'], fu_cohort['matched'], values=fu_cohort['person_id'], aggfunc=lambda x: len(x.unique()))
    # >>> matched              False  True
    # >>> ASC_B14               3729  5905
    # >>> ASC_B15_B16            294     0
    # >>> Previous_Publication   198   361
    # >>> SPARK                 2568  7007
    # >>> SPARK_pilot            115   350
    
    # none of the missing 294 ASC_B15_B16 samples are included in other studies. Some 
    # of their IDs look similar to the ASC nomeclature (e.g. 11379.p1 vs 11379-1, but 
    # this is a red herring, it's merely a similiar numerical scheme, they don't
    # have any matching de novos). Most samples have a de novo call (279 of 294), but
    # only 39% of those are coding, so overall we should only miss ~6 coding chrX
    # de novos (39% * 294 * 0.05 (fraction of genome in chrX)).
    ASC_B15_B16_missing = set(fu_cohort['person_id'][(fu_cohort['vcf_batch'] == 'ASC_B15_B16') & ~fu_cohort['matched']])
    sum(in_multiple_studies(cohort, x) for x in ASC_B15_B16_missing) / len(ASC_B15_B16_missing)
    len(set(fu[fu.person_id.isin(ASC_B15_B16_missing)].person_id))
    fu[fu.person_id.isin(ASC_B15_B16_missing)].Simplified_csq.value_counts()
    
    # 36.3% (1353 of 3729) of the missing ASC_B14 samples are represented in other
    # publications. Only 41% (1457) of the missing samples have a reported de novo in
    # Fu et al. Of those with a de novo call, >95% are coding, so it's not clear why
    # Zhou et al lacks a corresponding call.
    # NOTE: this is the potentially the most problematic discrepancy, but even
    # NOTE: this should only mean ~73 de novos missing from chrX (1457 * 0.05) 
    ASC_B14_missing = set(fu_cohort['person_id'][(fu_cohort['vcf_batch'] == 'ASC_B14') & ~fu_cohort['matched']])
    sum(in_multiple_studies(cohort, x) for x in ASC_B14_missing) / len(ASC_B14_missing)
    len(set(fu[fu.person_id.isin(ASC_B14_missing)].person_id))
    fu[fu.person_id.isin(ASC_B14_missing)].Simplified_csq.value_counts()
    
    # 57.1% (113 of 198) of the Previous_Publication samples are reported in other studies.
    # 70% have a de novo call. Of those with a de novo call, only 30% are coding.
    prev_pub_missing = set(fu_cohort['person_id'][(fu_cohort['vcf_batch'] == 'Previous_Publication') & ~fu_cohort['matched']])
    sum(in_multiple_studies(cohort, x) for x in prev_pub_missing) / len(prev_pub_missing)
    len(set(fu[fu.person_id.isin(prev_pub_missing)].person_id))
    fu[fu.person_id.isin(prev_pub_missing)].Simplified_csq.value_counts()
    
    # The 2568 missing SPARK samples have a good explanation. Half lack a de novo
    # call. Of those with a de novo call, only 10% are coding. Since Zhou et al
    # only includes coding variants, and has slightly different de novo calls 
    # these end up as missing from Zhou et al.
    spark_missing = set(fu_cohort['person_id'][(fu_cohort['vcf_batch'] == 'SPARK') & ~fu_cohort['matched']])
    sum(in_multiple_studies(cohort, x) for x in spark_missing) / len(spark_missing)
    len(set(fu[fu.person_id.isin(spark_missing)].person_id))
    fu[fu.person_id.isin(spark_missing)].Simplified_csq.value_counts()
    
    # None of the 115 SPARK_pilot missing samples are reported previously. 65% have 
    # a de novo call. Of those with a de novo call, only 6% are coding, which explains 
    # their omission from Zhou et al.
    spark_pilot_missing = set(fu_cohort['person_id'][(fu_cohort['vcf_batch'] == 'SPARK_pilot') & ~fu_cohort['matched']])
    sum(in_multiple_studies(cohort, x) for x in spark_pilot_missing) / len(prev_pub_missing)
    len(set(fu[fu.person_id.isin(spark_pilot_missing)].person_id))
    fu[fu.person_id.isin(spark_pilot_missing)].Simplified_csq.value_counts()
