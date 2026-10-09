# Elite 100m Freestyle Performance Analysis

A statistical analysis of elite men's and women's 100m freestyle swimming, focusing on pacing strategy, second-half performance deterioration, repeated athlete observations, and semifinal-to-final changes.

## Project Overview

This project analyzes elite 100m freestyle performances from major international swimming competitions from 2000 through 2025.

The analysis uses Python to collect, clean, validate, and analyze race-level data from the World Aquatics API.

The primary statistical question is:

**How does pacing behavior change between the semifinal and final of elite 100m freestyle competitions?**

Men and women are analyzed separately.

## Data

The dataset includes performances from:

- Olympic Games
- World Aquatics Championships
- FINA World Championships

The full database contains:

- 2,767 men's race observations
- 2,129 women's race observations
- 21 major international competitions

The primary elite analysis sample is restricted to semifinal and final performances with complete pacing data.

Primary sample sizes:

- Men: 407 performances
- Women: 431 performances

Because many swimmers appear multiple times across competitions and rounds, the analysis explicitly accounts for within-swimmer dependence.

## Key Variables

The main pacing measure is second-half dropoff:

```text
Dropoff (%) = ((Second 50m - First 50m) / First 50m) x 100
EDF
