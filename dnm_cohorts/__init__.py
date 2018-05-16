from pkg_resources import get_distribution

__version__ = get_distribution('dnm_cohorts').version

from dnm_cohorts.open_data import open_de_novos, open_cohort
