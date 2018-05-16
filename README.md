
#### dnm_cohorts

This small package collects sample information and de novo mutations from
published studies of de novo mutations in rare disease.

This also reconciles individuals and variants included in multiple studies, so
we don't double count individuals if they are present in multiple studies.

All of the information is obtained from the relevant supplementary data tables
associated with each journal publication.

#### Install
``` sh
pip install git+git://git.illumina.com/jeremymcrae/dnm_cohorts.git
```

#### Usage
The data files are included in the package, and can be loaded in python with:
``` python
from dnm_cohorts import open_de_novos, open_cohort

de_novos = open_de_novos()
cohort = open_cohort()
```

#### Build data files
``` sh
# to create a table of all individuals in the cohorts
dnm_cohorts --cohorts --output test.txt

# to create a table of all de novo mutations found in those individuals
dnm_cohorts --de-novos --output test.txt
```
