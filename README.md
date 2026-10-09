# Elite 100m Freestyle Performance Analysis

A statistical analysis of elite men's and women's 100m freestyle swimming, focusing on pacing strategy, second-half speed deterioration, repeated athlete observations, semifinal-to-final changes, and selected physical characteristics.

## Project Overview

This project analyzes elite 100m freestyle performances from major international long-course competitions from 2000 through 2025.

The analysis uses Python to collect, clean, validate, and analyze race-level data from the World Aquatics API.

The primary research question is:

**How does pacing behavior change between the semifinal and final of elite 100m freestyle competitions?**

Men and women are analyzed separately for the main analyses.

## Data

The dataset includes performances from:

- Olympic Games
- FINA World Championships
- World Aquatics Championships

The study covers 21 major international competitions from 2000 through 2025.

The complete race database contains:

- 2,767 men's race observations
- 2,129 women's race observations
- 1,167 unique male swimmers
- 824 unique female swimmers

The primary elite analysis sample is restricted to semifinal and final performances with complete 50 m split and final-time data.

Primary analysis sample:

- Men: 407 performances from 136 swimmers
- Women: 431 performances from 127 swimmers
- Combined: 838 elite performances

Because many swimmers appear repeatedly across rounds and competitions, the statistical analysis accounts for within-swimmer dependence.

## Key Variables

The main pacing variable is second-half percentage dropoff:

```text
Dropoff (%) = ((Second 50m - First 50m) / First 50m) x 100
A larger positive value indicates greater slowing during the second half of the race.
Additional variables include:
- Final 100 m time
- First 50 m split
- Second 50 m split
- Reaction time
- Athlete age
- Competition year
- Race round
- Athlete height
- Athlete weight
dropoff_percent is used as the primary pacing measure because alternative measures such as pacing ratio and absolute split difference are highly redundant with it.
## Main Findings
1. Semifinal-to-final pacing changes
Among swimmers who competed in both the semifinal and final of the same competition, second-half pacing deterioration increased in the final.
Men:
- Semifinal mean dropoff: 8.80%
- Final mean dropoff: 9.63%
- Mean increase: 0.82 percentage points
- Cohen's dz: 0.40
- 67.6% of swimmers showed greater dropoff in the final
Women:
- Semifinal mean dropoff: 7.11%
- Final mean dropoff: 8.02%
- Mean increase: 0.91 percentage points
- Cohen's dz: 0.53
- 70.1% of swimmers showed greater dropoff in the final
Bootstrap confidence intervals were fully above zero for both men and women.
2. Mechanism of the semifinal-to-final change
The larger final-round dropoff appears to be driven primarily by a more aggressive opening 50 m.
Men:
- First 50 m: 0.133 s faster in finals
- Second 50 m: 0.043 s slower
- Final time: 0.090 s faster overall
Women:
- First 50 m: 0.164 s faster in finals
- Second 50 m: 0.059 s slower
- Final time: 0.105 s faster overall
This pattern suggests that swimmers reach the final and swim faster overall, but do so partly by increasing first-half speed and accepting greater second-half deterioration.
These are observational associations and should not be interpreted as causal effects.
3. Long-term pacing trends
Simple OLS models suggested a decline in male dropoff over time, but this association weakened after accounting for repeated observations from the same swimmer.
Population-average GEE models found:
- Men: no statistically significant long-term pacing trend
- Women: no statistically significant long-term pacing trend
This indicates that apparent time trends can be sensitive to the statistical treatment of repeated athlete observations.
4. Height and performance
Physical characteristics were enriched using Wikidata.
Height data were available for:
- 86 of 136 men
- 89 of 127 women
After accounting for competition year, age, reaction time, race round, and repeated athlete observations:
Men:
- No clear association between height and final time
- No clear association between height and first or second 50 m performance
Women:
- Greater height was associated with faster final times
- Greater height was especially associated with faster second 50 m performance
Formal height-by-sex interaction tests were significant for:
- Final time
- Second 50 m
No significant interaction was detected for:
- First 50 m
- Percentage dropoff
These findings are observational and may be affected by incomplete historical physical-data coverage and residual confounding.
## Statistical Methods
The project uses:
- Descriptive statistics
- Pearson correlations
- Paired t-tests
- Wilcoxon signed-rank tests
- Bootstrap confidence intervals
- OLS regression
- Cluster-robust standard errors
- Mixed-effects models
- Generalized Estimating Equations
- Interaction models
- Missing-data diagnostics
GEE models are used as the primary population-average approach when repeated observations from the same swimmer must be accounted for.
## Data Quality
The cleaning pipeline performs:
- Duplicate detection
- Swimming-time parsing
- Split consistency checks
- Plausibility checks
- Missing-value reporting
- Outlier inspection
World Aquatics race times may appear in either seconds format or minute-second format, so the cleaning pipeline standardizes both formats before analysis.
Extreme pacing observations are concentrated primarily in preliminary heats and do not enter the primary semifinal/final analysis sample.
## Physical Data
Athlete physical characteristics were enriched using Wikidata.
The enrichment pipeline includes:
- Exact name matching
- Fuzzy name matching
- Manual validation of uncertain matches
- Height and weight plausibility checks
- Missingness analysis
Final physical-data coverage:
- 263 athletes in the primary sample
- 175 with height data
- 137 with weight data
- 242 validated Wikidata matches
Physical characteristics should be interpreted cautiously because historical athlete profiles may not always represent measurements taken at the exact time of competition.
## Project Structure
elite-100m-freestyle-analysis/
|
├── data/
│   ├── raw/
│   └── processed/
|
├── outputs/
│   ├── figures/
│   └── tables/
|
├── src/
│   ├── 01_collect_data.py
│   ├── 02_clean_data.py
│   ├── 03_build_analysis_sample.py
│   ├── 04_descriptive_analysis.py
│   ├── 05_pacing_models.py
│   ├── 06_semifinal_final_analysis.py
│   ├── 30_physical_data_enrichment.py
│   └── 31_physical_performance_analysis.py
|
├── README.md
├── requirements.txt
└── .gitignore

## Reproducible Pipeline
Run the main analysis in order:
python src/01_collect_data.py
python src/02_clean_data.py
python src/03_build_analysis_sample.py
python src/04_descriptive_analysis.py
python src/05_pacing_models.py
python src/06_semifinal_final_analysis.py

Then run the physical-data branch:
python src/30_physical_data_enrichment.py
python src/31_physical_performance_analysis.py

## Main Outputs
Key figures include:
- Paired semifinal-to-final pacing trajectories
- Semifinal-to-final difference distributions
- Main pacing result figure
- Semifinal-to-final mechanism figure
Key tables include:
- Descriptive statistics
- Correlation analysis
- Pacing model summaries
- Semifinal-final paired results
- Bootstrap estimates
- Height-performance GEE models
- Height-by-sex interaction models
- Physical-performance correlations
## Interpretation
The strongest result in the project is the consistent semifinal-to-final pacing shift.
Elite swimmers tend to swim the final with a faster opening 50 m and greater second-half slowing than in the semifinal, while still producing a faster overall 100 m time.
This suggests an important tactical distinction between qualification and medal-round racing in elite sprint freestyle.
## Data Sources
Primary race data:
- World Aquatics API
Physical athlete data:
- Wikidata
## Technologies
- Python
- pandas
- NumPy
- SciPy
- statsmodels
- matplotlib
- requests

## Author
Daniel Eichel
