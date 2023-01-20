
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

The package contains a dataset of de novos on their original genome build (the
default), as well as a dataset lifted to GRCh37 and a dataset lifted to GRCh38.

#### Cohorts
reference   |   year   |  unique individuals  |   phenotype   |   assay   | deprecated
----        |   ----   |        ----          |   ----        |   ----    |   -----
[De Ligt _et al_. _N Engl J Med_ 367:1921-1929](https://doi.org/10.1056/NEJMoa1206524)        | 2012 |   100 | intellectual disability    |    exome    |    no
[Iossifov _et al_. _Neuron_ 74:285-299](https://doi.org/10.1016/j.neuron.2012.04.009)         | 2012 |   686 (343 asd, 343 unaffected)    | autism spectrum disorder, unaffected siblings   |    exome    |    no
[O'Roak _et al_. _Nature_ 485:246-250](https://doi.org/10.1038/nature10989)                   | 2012 |   206 | autism spectrum disorder   |    exome    |    no
[Rauch _et al_. _Lancet_ 380:1674-1682](https://doi.org/10.1016/S0140-6736%2812%2961480-9)    | 2012 |    51 | intellectual disability    |    exome    |    no
[Sanders _et al_. _Nature_ 485:237-241](https://doi.org/10.1038/nature10945)                  | 2012 |   452 (238 asd, 214 unaffected)    | autism spectrum disorder, unaffected siblings   |    exome    |    no
[Epi4K Consortium. _Nature_ 501:217-221](https://doi.org/10.1038/nature12439)                 | 2013 |   264 | epilepsy                   |    exome    |    no
[EuroEPINOMICS-RES Consortium. _AJHG_ 95:360-370](https://doi.org/10.1016/j.ajhg.2014.08.013) | 2014 |    92 | epilepsy                   |    exome    |    no
[Gilissen _et al_. _Nature_ 511:344-347](https://doi.org/10.1038/nature13394)                 | 2014 |     0 | intellectual disability    |    exome    |    no, but only extends De ligt et al
[De Rubeis _et al_. _Nature_ 515:209-215](https://doi.org/10.1038/nature13772)                | 2014 |  1604 (1443 asd, 161 unaffected)   | autism spectrum disorder, unaffected siblings   |    exome    |    no
[Iossifov _et al_. _Nature_ 498:216-221](https://doi.org/10.1038/nature13908)                 | 2014 |  3095 (1726 asd, 1369 unaffected)  | autism spectrum disorder, unaffected siblings   |    exome    |    no
[Sanders _et al_. _Neuron_ 87:1215-1233](https://doi.org/10.1016/j.neuron.2015.09.016)        | 2015 |   750 (314 asd, 436 unaffected)    | autism spectrum disorder, unaffected siblings   |    exome    |    no
[Homsy _et al_. _Science_ 350:1262-1266](https://doi.org/10.1126/science.aac9396)             | 2015 |  1213 | congenital heart disease   |    exome    |   yes, superseded by Jin et al cohort
[Lelieveld _et al_. _Nature Neuroscience_ 19:1194-1196](https://doi.org/10.1038/nn.4352)      | 2016 |   820 | intellectual disability    |    exome    |   yes, superseded by Kaplanis et al cohort
[McRae _et al_. _Nature_ 542:433-438](https://doi.org/10.1038/nature21062)                    | 2017 |  4293 | intellectual disability    |    exome    |   yes, superseded by Kaplanis et al cohort
[Jónsson _et al_. _Nature_ 549:519-522](https://doi.org/10.1038/nature24018)                  | 2017 |  1458 | unaffected                 |    genome (no chrX in males)    |    yes
[Jin _et al_. _Nature Genetics_ 49:1593-1601](https://doi.org/10.1038/ng.3970)                | 2017 |  2465 | congenital heart disease   |    exome    |    no
[Yuen _et al_. _Nature Neuroscience_ 20:602-611](https://doi.org/10.1038/nn.4524)             | 2017 |  5265 | autism spectrum disorder   |   genome    |    no
[An _et al_. _Science_ 362:eaat6576](https://doi.org/10.1126/science.aat6576)                 | 2018 |  1902 affected, 1902 unaffected    | autism spectrum disorder, unaffected siblings   |    genome    |    no
[Halldorsson _et al_. _Science_](https://doi.org/10.1126/science.aau1043)                     | 2019 |  2976 | unaffected, supersedes Jónsson et al   |    genome    |    no
[Kaplanis _et al_. _Nature_](https://doi.org/10.1038/s41586-020-2832-5)                       | 2019 | 31058 | intellectual disability, supersedes Lelieveld et al and McRae et al cohorts   |    exome    |    no
[Fu _et al._ _Nature Genetics_ 54:1320-1331](https://doi.org/10.1038/s41588-022-01104-0)      | 2022 | 42607 | autism spectrum disorder   |    exome (no chrX)  |    no, but Fu et al and Zhou et al mostly overlap
[Zhou _et al._ _Nature Genetics_ 54:1305-1319](https://doi.org/10.1038/s41588-022-01148-2)    | 2022 | 42607 | autism spectrum disorder   |    exome    |    yes, by Fu et al, because Fu et al include all sample IDs

#### Excluded cohorts
We exclude some published cohorts with de novo mutations, for the reasons below:
 - Helbig _et al_ in [_Genetics in Medicine_ 18:898-905](https://doi.org/10.1038/gim.2015.186). This study only reported the likely pathogenic de novo mutations.
 - Goldman _et al._ in [_Nature Genetics_ 48:935-939](https://doi.org/10.1038/ng.3597). This study includes monozygotic twins, so some de novo mutations are not independent, but does not include sample or family IDs that would permit exclusion of the monozygotic twins.
 - Goldmann _et al._ in [_Nature Genetics_ 50:487-492](https://doi.org/10.1038/s41588-018-0071-6). This study only reported clustered DNMs, so not representative of all coding DNMs.
