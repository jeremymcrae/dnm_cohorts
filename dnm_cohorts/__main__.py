
import itertools
import argparse
import asyncio
import sys
import os
import logging
from itertools import groupby

from dnm_cohorts.ensembl import get_consequences
from dnm_cohorts.cohorts import (open_de_ligt_cohort, open_rauch_cohort,
    open_de_rubeis_cohort, open_epi4k_ajhg_cohort, open_iossifov_nature_cohort,
    open_iossifov_neuron_cohort, open_oroak_cohort, open_sanders_nature_cohort,
    open_sanders_neuron_cohort, open_lelieveld_cohort, open_mcrae_nature_cohort,
    open_homsy_science_cohort, open_an_science_cohort, kaplanis_biorxiv_cohort)
from dnm_cohorts.de_novos import (de_ligt_nejm_de_novos,
    de_rubeis_nature_de_novos, epi4k_ajhg_de_novos, gilissen_nature_de_novos,
    iossifov_neuron_de_novos, iossifov_nature_de_novos, lelieveld_nn_de_novos,
    mcrae_nature_de_novos, oroak_nature_de_novos, rauch_lancet_de_novos,
    sanders_nature_de_novos, sanders_neuron_de_novos, homsy_science_de_novos,
    an_science_de_novos, kaplanis_biorxiv_de_novos)
from dnm_cohorts.convert_pdf_table import flatten
from dnm_cohorts.exclude_duplicates import drop_inperson_duplicates
from dnm_cohorts.de_novo import DeNovo
from dnm_cohorts.rate_limiter import RateLimiter

def get_options():
    parser = argparse.ArgumentParser()
    parent = argparse.ArgumentParser(add_help=False)
    
    parent.add_argument('--output', default=sys.stdout, help='where to save output')
    parent.add_argument('--log', default=sys.stderr, help='where to write log output')
    
    subparsers = parser.add_subparsers()
    de_novos = subparsers.add_parser('de-novos', parents=[parent],
        description='Gets de novo mutations from publically available datasets.')
    de_novos.add_argument('--de-novos', default=True)
    de_novos.add_argument('--cohorts', default=False)
    cohort = subparsers.add_parser('cohort', parents=[parent],
        description='Gets cohort info for de novo datasets')
    cohort.add_argument('--cohorts', default=True)
    cohort.add_argument('--de-novos', default=False)
    lifter = subparsers.add_parser('lift', parents=[parent],
        description='Converts de novo mutations to a different genome build')
    lifter.add_argument('--input', required=True, help='path to input de novos')
    lifter.add_argument('--to', required=True,
        help='genome build to lift variant on to. Variants start with a build' \
             'associated with them, so no need to supply a from-build')
    lifter.add_argument('--cohorts', default=False)
    lifter.add_argument('--de-novos', default=False)
    
    args = parser.parse_args()
    
    try:
        args.output = open(args.output, 'w')
    except TypeError:
        pass
    
    try:
        args.log = open(args.log, 'w')
    except TypeError:
        pass
    
    if hasattr(args, 'input'):
        args.input = open(args.input, 'r')
    
    return args

def get_cohorts(output, header):
    ''' get list of all individuals in all cohorts
    '''
    # open ASD cohort info, then drop duplicate samples from the ASD cohorts
    asd = [open_sanders_neuron_cohort(), open_de_rubeis_cohort(),
        open_iossifov_nature_cohort(), open_iossifov_neuron_cohort(),
        open_oroak_cohort(), open_sanders_nature_cohort(),
        open_an_science_cohort()]
    
    for a, b in itertools.combinations(asd, 2):
        a -= b
    
    # TODO: what about the 1 in 1000 people with differing sex between studies?
    # TODO: I've kept them for now, since they are negligle and conservative.
    samples = asd + [open_de_ligt_cohort(), open_rauch_cohort(),
        open_epi4k_ajhg_cohort(), open_homsy_science_cohort(),
        kaplanis_biorxiv_cohort()]
    
    _ = output.write('\t'.join(header) + '\n')
    for x in flatten(samples):
        _ = output.write(str(x) + '\n')

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

async def get_de_novos(output, header):
    """ get list of all de novos in all cohorts
    """
    async with RateLimiter(15) as limiter:
        # open ASD cohort info, then drop duplicate samples from the ASD cohorts
        asd = [sanders_neuron_de_novos(), de_rubeis_nature_de_novos(),
            iossifov_nature_de_novos(), iossifov_neuron_de_novos(limiter),
            oroak_nature_de_novos(limiter), sanders_nature_de_novos(limiter),
            an_science_de_novos()]
        asd = await asyncio.gather(*asd)
        
        for a, b in itertools.combinations(asd, 2):
            # remove the easy matches
            a -= b
        
        asd = remove_duplicate_dnms(reversed(asd))
        non_asd = [de_ligt_nejm_de_novos(limiter), gilissen_nature_de_novos(limiter),
            epi4k_ajhg_de_novos(limiter), homsy_science_de_novos(),
            rauch_lancet_de_novos(limiter), kaplanis_biorxiv_de_novos(limiter)]
        
        cohorts = list(asd) + flatten(await asyncio.gather(*non_asd))
        cohorts = await get_consequences(limiter, cohorts)
        
        _ = output.write('\t'.join(header) + '\n')
        for x in drop_inperson_duplicates(cohorts):
            _ = output.write(str(x) + '\n')

def change_build(input, output, build, header):
    ''' shift variants onto a new genome build
    '''
    _ = input.readline()
    _ = output.write('\t'.join(header) + '\n')
    for line in input:
        var = DeNovo(*line.strip('\n').split('\t'))
        if not var:
            continue
        remapped = var.to_build(build)
        if remapped:
            _ = output.write(str(remapped) + '\n')

async def _main():
    args = get_options()
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(stream=args.log, format=FORMAT, level=logging.INFO)
    
    if args.cohorts:
        header = ['person_id', 'sex', 'phenotype']
        get_cohorts(args.output, header)
    elif args.de_novos:
        header = ['person_id', 'chrom', 'pos', 'ref', 'alt', 'study',
            'confidence', 'build', 'symbol', 'consequence']
        await get_de_novos(args.output, header)
    else:
        header = ['person_id', 'chrom', 'pos', 'ref', 'alt', 'study',
            'confidence', 'build', 'symbol', 'consequence']
        change_build(args.input, args.output, args.to, header)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main())

if __name__ == '__main__':
    main()
