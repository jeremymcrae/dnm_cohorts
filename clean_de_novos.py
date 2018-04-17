

import pandas
import gzip

de_novos_path = '/home/jmcrae/apps/missense_vus/data/de_novos.default.txt'

variants = pandas.read_table(de_novos_path)

variants['study_phenotype'][variants['study_code'].isin(['sanders_nature_2012',
    'iossifov_neuron_2012'])] = 'unaffected_sibling'

variants = variants.rename(columns={'start_pos': 'pos', 'ref_allele': 'ref',
    'alt_allele': 'alt', 'study_phenotype': 'phenotype', 'hgnc': 'symbol',
    'study_code': 'study'})
studies = sorted(set(variants.study))
recode = dict(zip(studies, studies))
recode['SSC_Iossifov_2014'] = 'iossifov_nature_2014'
recode['ASC_DeRubeis'] = 'derubeis_nature_2014'
recode['SSC_Dong_2014'] = 'dong_cell_reports_2014'
variants['study'] = variants['study'].map(recode)

variants['phenotype'][variants.study == 'mcrae_nature_2017'] = 'developmental_disorders'
variants['phenotype'][variants.study == 'mcrae_nature_2017'] = 'developmental_disorders'
variants['phenotype'][variants['phenotype'] == 'normal_iq_autism'] = 'autism'

variants = variants[['study', 'person_id', 'chrom', 'pos', 'ref', 'alt', 'symbol', 'consequence']]

with gzip.open('de_novos.txt.gz', 'wt') as output:
    variants.to_csv(output, sep='\t', index=False, na_rep='NA')
