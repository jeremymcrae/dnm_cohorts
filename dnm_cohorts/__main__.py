
import itertools
import argparse
import trio
import sys
import os
import logging
from itertools import groupby

from dnm_cohorts.ensembl import get_consequences
from dnm_cohorts.cohorts import (open_de_ligt_cohort, open_rauch_cohort,
    open_de_rubeis_cohort, open_epi4k_ajhg_cohort, open_iossifov_nature_cohort,
    open_iossifov_neuron_cohort, open_oroak_cohort, open_sanders_nature_cohort,
    open_sanders_neuron_cohort, open_lelieveld_cohort, open_mcrae_nature_cohort,
    open_homsy_science_cohort, open_jonsson_nature_cohort,
    open_jin_nature_genetics_cohort, open_an_science_cohort,
    kaplanis_nature_cohort)
from dnm_cohorts.de_novos import (de_ligt_nejm_de_novos,
    de_rubeis_nature_de_novos, epi4k_ajhg_de_novos, gilissen_nature_de_novos,
    iossifov_neuron_de_novos, iossifov_nature_de_novos, lelieveld_nn_de_novos,
    mcrae_nature_de_novos, oroak_nature_de_novos, rauch_lancet_de_novos,
    sanders_nature_de_novos, sanders_neuron_de_novos, homsy_science_de_novos,
    jonsson_nature_de_novos, jin_nature_genetics_de_novos, an_science_de_novos,
    kaplanis_nature_de_novos)
from dnm_cohorts.convert_pdf_table import flatten
from dnm_cohorts.exclude_duplicates import drop_inperson_duplicates
from dnm_cohorts.de_novo import DeNovo
from dnm_cohorts.rate_limiter import RateLimiter

def get_options():
    parser = argparse.ArgumentParser(add_help=False)
    
    parser.add_argument('--output', type=argparse.FileType('wt'),
        default=sys.stdout, help='where to save output')
    parser.add_argument('--log', type=argparse.FileType('wt'),
        default=sys.stderr, help='where to write log output')
    
    subparsers = parser.add_subparsers()
    de_novos = subparsers.add_parser('de-novos', parents=[parser],
        description='Gets de novo mutations from publically available datasets.')
    de_novos.set_defaults(func=get_de_novos)
    
    cohort = subparsers.add_parser('cohort', parents=[parser],
        description='Gets cohort info for de novo datasets')
    cohort.set_defaults(func=get_cohorts)
    
    lifter = subparsers.add_parser('lift', parents=[parser],
        description='Converts de novo mutations to a different genome build')
    lifter.add_argument('--input', type=argparse.FileType('rt'),
        required=True, help='path to input de novos')
    lifter.add_argument('--to', required=True,
        help='genome build to lift variant on to. Variants start with a build' \
             'associated with them, so no need to supply a from-build')
    lifter.set_defaults(func=change_build)
    
    return parser.parse_args()

def merge_duplicate_persons(person_lists):
    ''' merge duplicate persons
    '''
    # convert to dicts to be able to set new merged persons
    person_lists = [dict(zip(x, x)) for x in person_lists]
    for a, b in itertools.combinations(person_lists, 2):
        for x in set(a) & set(b):
            x.phenotype = sorted(set(a[x].phenotype + b[x].phenotype))
            x.studies = sorted(set(a[x].studies + b[x].studies))
            del a[x]
            del b[x]
            a[x] = x
    
    person_lists = [set(x) for x in person_lists]
    for a, b in itertools.combinations(person_lists, 2):
        a -= b
    
    return person_lists

async def get_cohorts(args):
    ''' get list of all individuals in all cohorts
    '''
    header = ['person_id', 'sex', 'phenotype', 'studies']
    yield '\t'.join(header) + '\n'
    # open ASD cohort info, then drop duplicate samples from the ASD cohorts
    asd = [open_sanders_neuron_cohort(), open_de_rubeis_cohort(),
        open_iossifov_nature_cohort(), open_iossifov_neuron_cohort(),
        open_oroak_cohort(), open_sanders_nature_cohort(),
        open_an_science_cohort()]
    
    # TODO: what about the 1 in 1000 people with differing sex between studies?
    # TODO: I've kept them for now, since they are negligle and conservative.
    samples = asd + [open_de_ligt_cohort(), open_rauch_cohort(),
        open_epi4k_ajhg_cohort(), open_jonsson_nature_cohort(),
        open_jin_nature_genetics_cohort(), kaplanis_nature_cohort()]
    
    samples = merge_duplicate_persons(samples)
    for x in flatten(samples):
        yield str(x) + '\n'

def remove_duplicate_dnms(cohorts):
    """ only include unique variants
    """
    
    unique = set()
    for id, group in groupby(flatten(cohorts), key=lambda x: x.person_id):
        # within variants for an individual, check to see if any are the same
        # variant by seeing if any already included overlap the same range.
        # We can't just check for inclusion inside the set, as that would use
        # the position, not the range.
        shrunken = set()
        for var in group:
            if not any( var == x for x in shrunken ):
                shrunken.add(var)
        unique |= shrunken
    
    return unique

async def get_de_novos(args):
    """ get list of all de novos in all cohorts
    """
    header = ['person_id', 'chrom', 'pos', 'ref', 'alt', 'study',
        'confidence', 'build', 'symbol', 'consequence']
    yield '\t'.join(header) + '\n'
    async with RateLimiter(14) as limiter:
        # open ASD cohort info, then drop duplicate samples from the ASD cohorts
        asd = []
        async with trio.open_nursery() as nursery:
            nursery.start_soon(sanders_neuron_de_novos, asd)
            nursery.start_soon(de_rubeis_nature_de_novos, asd)
            nursery.start_soon(iossifov_nature_de_novos, asd)
            nursery.start_soon(iossifov_neuron_de_novos, asd, limiter)
            nursery.start_soon(oroak_nature_de_novos, asd, limiter)
            nursery.start_soon(sanders_nature_de_novos, asd, limiter)
            nursery.start_soon(an_science_de_novos, asd)
        
        for a, b in itertools.combinations(asd, 2):
            # remove the easy matches
            a -= b
        
        asd = remove_duplicate_dnms(reversed(asd))
        non_asd = []
        async with trio.open_nursery() as nursery:
            nursery.start_soon(de_ligt_nejm_de_novos, non_asd, limiter)
            nursery.start_soon(gilissen_nature_de_novos, non_asd, limiter)
            nursery.start_soon(epi4k_ajhg_de_novos, non_asd, limiter)
            nursery.start_soon(jin_nature_genetics_de_novos, non_asd)
            nursery.start_soon(rauch_lancet_de_novos, non_asd, limiter)
            nursery.start_soon(jonsson_nature_de_novos, non_asd)
            nursery.start_soon(kaplanis_nature_de_novos, non_asd, limiter)
        
        cohorts = list(asd) + flatten(non_asd)
        cohorts = await get_consequences(limiter, cohorts)
        
        for x in drop_inperson_duplicates(cohorts):
            yield str(x) + '\n'

async def change_build(args):
    ''' shift variants onto a new genome build
    '''
    header = ['person_id', 'chrom', 'pos', 'ref', 'alt', 'study',
        'confidence', 'build', 'symbol', 'consequence']
    yield '\t'.join(header) + '\n'
    _ = args.input.readline()
    _ = args.output.write('\t'.join(header) + '\n')
    for line in args.input:
        var = DeNovo(*line.strip('\n').split('\t'))
        if not var:
            continue
        yield str(var.to_build(args.to)) + '\n'

async def _main():
    args = get_options()
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(stream=args.log, format=FORMAT, level=logging.INFO)
    
    async for x in args.func(args):
        _ = args.output.write(x)

def main():
    trio.run(_main)

if __name__ == '__main__':
    main()
