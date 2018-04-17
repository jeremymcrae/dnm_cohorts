
import itertools
import argparse
import sys

from dnm_cohorts.cohorts.de_ligt_nejm import open_de_ligt_cohort
from dnm_cohorts.cohorts.rauch_lancet import open_rauch_cohort
from dnm_cohorts.cohorts.de_rubeis_nature import open_de_rubeis_cohort
from dnm_cohorts.cohorts.epi4k_nature import open_epi4k_nature_cohort
from dnm_cohorts.cohorts.iossifov_nature import open_iossifov_nature_cohort
from dnm_cohorts.cohorts.iossifov_neuron import open_iossifov_neuron_cohort
from dnm_cohorts.cohorts.oroak_nature import open_oroak_cohort
from dnm_cohorts.cohorts.sanders_nature import open_sanders_nature_cohort
from dnm_cohorts.cohorts.sanders_neuron import open_sanders_neuron_cohort
from dnm_cohorts.cohorts.lelieveld_nature_neuroscience import open_lelieveld_cohort
from dnm_cohorts.cohorts.mcrae_nature import open_mcrae_nature_cohort

def get_options():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=sys.stdout, help='path to save output to')
    
    args = parser.parse_args()
    
    try:
        args.output = open(args.output, 'w')
    except TypeError:
        pass
    
    return args

def main():
    args = get_options()
    
    de_ligt = open_de_ligt_cohort()
    rauch_lancet = open_rauch_cohort()
    de_rubeis = open_de_rubeis_cohort()
    epi4k = open_epi4k_nature_cohort()
    iossifov_nature = open_iossifov_nature_cohort()
    iossifov_neuron = open_iossifov_neuron_cohort()
    oroak_nature = open_oroak_cohort()
    sanders_nature = open_sanders_nature_cohort()
    sanders_neuron = open_sanders_neuron_cohort()
    lelieveld_nn = open_lelieveld_cohort()
    mcrae_nature = open_mcrae_nature_cohort()
    
    # drop duplicate samples from the ASD cohorts
    asd_cohorts = [de_rubeis, iossifov_nature, iossifov_neuron, oroak_nature,
        sanders_nature, sanders_neuron]
        
    for a, b in itertools.combinations(asd_cohorts, 2):
        a -= b
    
    # TODO: what about the 1 in 1000 people with differing sex between studies?
    # TODO: I've kept them for now, since they are negligle and conservative.
    samples = asd_cohorts + [de_ligt, rauch_lancet, epi4k, lelieveld_nn, mcrae_nature]
    
    _ = args.output.write('person_id\tsex\tphenotype\tstudy\n')
    for cohort in samples:
        for sample in cohort:
            _ = args.output.write(str(sample))

if __name__ == '__main__':
    main()
