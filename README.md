
#### dnm_cohorts

This small package collects sample information and de novo mutations from
published studies of de novo mutations in rare disease.

This also reconciles individuals and variants included in multiple studies, so
we don't double count individuals if they are present in multiple studies.

All of the information is obtained from the relevant supplementary data tables
associated with each journal publication. Where a study has collected healthy
controls (e.g. unaffected siblings), the phenotype of the healthy controls is
'unaffected'.

#### Install
``` sh
pip install git+git://github.com/jeremymcrae/dnm_cohorts.git
```

#### Usage
The data files are included in the package, and can be loaded in python with:
``` python
from dnm_cohorts import de_novos, cohort
```

#### Build data files
``` sh
# to create a table of all individuals in the cohorts
dnm_cohorts --cohorts --output test.txt

# to create a table of all de novo mutations found in those individuals
dnm_cohorts --de-novos --output test.txt
```

#### Cohorts
reference   |   year   |  unique individuals  |   phenotype
----        |   ----   |        ----       |   ----
[De Ligt _et al_. _N Engl J Med_ 367:1921-1929](https://doi.org/10.1056/NEJMoa1206524)        | 2012 |  100 | intellectual disability
[Iossifov _et al_. _Neuron_ 74:285-299](https://doi.org/10.1016/j.neuron.2012.04.009)         | 2012 |  686 (343 asd, 343 unaffected) | autism spectrum disorder,  unaffected siblings
[O'Roak _et al_. _Nature_ 485:246-250](https://doi.org/10.1038/nature10989)                   | 2012 |  206 | autism spectrum disorder
[Rauch _et al_. _Lancet_ 380:1674-1682](https://doi.org/10.1016/S0140-6736%2812%2961480-9)    | 2012 |   51 | intellectual disability
[Sanders _et al_. _Nature_ 485:237-241](https://doi.org/10.1038/nature10945)                  | 2012 |  452 (238 asd, 214 unaffected) | autism spectrum disorder,  unaffected siblings
[Epi4K Consortium. _Nature_ 501:217-221](https://doi.org/10.1038/nature12439)                 | 2013 |  264 | epilepsy
[De Rubeis _et al_. _Nature_ 515:209-215](https://doi.org/10.1038/nature13772)                | 2013 | 1604 (1443 asd, 161 unaffected) | autism spectrum disorder, unaffected siblings
[EuroEPINOMICS-RES Consortium. _AJHG_ 95:360-370](https://doi.org/10.1016/j.ajhg.2014.08.013) | 2014 |   92 | epilepsy
[Gilissen _et al_. _Nature_ 511:344-347](https://doi.org/10.1038/nature13394)                 | 2014 |    0 | intellectual disability
[Iossifov _et al_. _Nature_ 498:216-221](https://doi.org/10.1038/nature13908)                 | 2014 | 3095 (1726 asd, 1369 unaffected) | autism spectrum disorder, unaffected siblings
[Sanders _et al_. _Neuron_ 87:1215-1233](https://doi.org/10.1016/j.neuron.2015.09.016)        | 2015 |  750 (314 asd, 436 unaffected) | autism spectrum disorder, unaffected siblings
[Homsy _et al_. _Science_ 350:1262-1266](https://doi.org/10.1126/science.aac9396)             | 2015 | 1213 | congenital heart disease
[Lelieveld _et al_. _Nature Neuroscience_ 19:1194-1196](https://doi.org/10.1038/nn.4352)      | 2016 |  820 | intellectual disability
[McRae _et al_. _Nature_ 19:1194-1196](https://doi.org/10.1038/nature21062)                   | 2017 | 4293 | intellectual disability
