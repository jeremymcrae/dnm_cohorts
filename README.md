
#### dnm_cohorts

This small package collects sample information from published studies of de novo
mutations in rare disease. This doesn't collect any of the de novo mutations,
but instead focuses on identifying all individuals in the studies, so that we
can have an accurate numbers of individuals for different phenotypes. This also
attempts to reconcile individuals included in multiple studies, so we don't
double count individuals if they are present in multiple studies.

All of the information is obtained from the relevant supplementary data tables
associated with each journal publication.

#### Install
``` sh
pip install git+git://git.illumina.com/jeremymcrae/dnm_cohorts.git
```

#### Run
``` sh
dnm_cohorts --output test.txt
```
