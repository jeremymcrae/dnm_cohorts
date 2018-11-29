
import itertools
import argparse
import sys
import os
import logging

from dnm_cohorts.ensembl import cq_and_symbol
from dnm_cohorts.cohorts import (open_de_ligt_cohort, open_rauch_cohort,
    open_de_rubeis_cohort, open_epi4k_ajhg_cohort, open_iossifov_nature_cohort,
    open_iossifov_neuron_cohort, open_oroak_cohort, open_sanders_nature_cohort,
    open_sanders_neuron_cohort, open_lelieveld_cohort, open_mcrae_nature_cohort,
    open_homsy_science_cohort)
from dnm_cohorts.de_novos import (de_ligt_nejm_de_novos,
    de_rubeis_nature_de_novos, epi4k_ajhg_de_novos, gilissen_nature_de_novos,
    iossifov_neuron_de_novos, iossifov_nature_de_novos, lelieveld_nn_de_novos,
    mcrae_nature_de_novos, oroak_nature_de_novos, rauch_lancet_de_novos,
    sanders_nature_de_novos, sanders_neuron_de_novos, homsy_science_de_novos)
from dnm_cohorts.convert_pdf_table import flatten
from dnm_cohorts.exclude_duplicates import drop_inperson_duplicates

def get_options():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--de-novos', default=False, action='store_true')
    group.add_argument('--cohorts', default=False, action='store_true')
    
    parser.add_argument('--output', default=sys.stdout, help='where to save output')
    parser.add_argument('--log', default=os.devnull, help='where to write log output')
    
    args = parser.parse_args()
    
    try:
        args.output = open(args.output, 'w')
    except TypeError:
        pass
    
    return args

def open_cohorts():
    ''' get list of all individuals in all cohorts
    '''
    # open ASD cohort info, then drop duplicate samples from the ASD cohorts
    asd = [open_sanders_neuron_cohort(), open_de_rubeis_cohort(),
        open_iossifov_nature_cohort(), open_iossifov_neuron_cohort(),
        open_oroak_cohort(), open_sanders_nature_cohort()]
    
    for a, b in itertools.combinations(asd, 2):
        a -= b
    
    # TODO: what about the 1 in 1000 people with differing sex between studies?
    # TODO: I've kept them for now, since they are negligle and conservative.
    samples = asd + [open_de_ligt_cohort(), open_rauch_cohort(),
        open_epi4k_ajhg_cohort(), open_homsy_science_cohort(),
        open_lelieveld_cohort(), open_mcrae_nature_cohort()]
    
    return samples

def remove_duplicate_dnms(cohorts):
    """ only include unique variants
    """
    
    shrunken = set()
    for var in flatten(cohorts):
        if not any( var == x for x in shrunken ):
            shrunken.add(var)
    
    return shrunken

def open_de_novos():
    """ get list of all de novos in all cohorts
    """
    # open ASD cohort info, then drop duplicate samples from the ASD cohorts
    asd = [sanders_neuron_de_novos(), de_rubeis_nature_de_novos(),
        iossifov_nature_de_novos(), iossifov_neuron_de_novos(),
        oroak_nature_de_novos(), sanders_nature_de_novos()]
    
    for a, b in itertools.combinations(asd, 2):
        # remove the easy matches
        a -= b
    
    asd = remove_duplicate_dnms(reversed(asd))
    
    cohorts = [asd] + [de_ligt_nejm_de_novos(), gilissen_nature_de_novos(),
        epi4k_ajhg_de_novos(), homsy_science_de_novos(),
        lelieveld_nn_de_novos(), rauch_lancet_de_novos(), mcrae_nature_de_novos()]
    
    return drop_inperson_duplicates(cohorts)

def main():
    args = get_options()
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(filename=args.log, format=FORMAT, level=logging.INFO)
    
    if args.cohorts:
        data = open_cohorts()
        header = ['person_id', 'sex', 'phenotype']
    else:
        data = open_de_novos()
        header = ['person_id', 'chrom', 'pos', 'ref', 'alt', 'study',
            'confidence', 'symbol', 'consequence']
    
    _ = args.output.write('\t'.join(header) + '\n')
    for cohort in data:
        for x in cohort:
            if args.de_novos:
                x.consequence, x.symbol = cq_and_symbol(x.chrom, x.pos, x.ref, x.alt)
            
            _ = args.output.write(str(x) + '\n')

if __name__ == '__main__':
    main()
