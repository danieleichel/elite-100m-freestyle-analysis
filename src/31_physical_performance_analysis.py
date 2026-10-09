import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf

from pathlib import Path
from scipy.stats import (
    pearsonr,
    spearmanr,
    ttest_ind,
    ttest_rel,
    wilcoxon
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MEN_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "men"
    / "men_analysis_sample.csv"
)

WOMEN_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "women"
    / "women_analysis_sample.csv"
)

PHYSICAL_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "athlete_master_physical_clean.csv"
)

CORRELATION_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "physical_performance_correlations.csv"
)

GEE_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "height_performance_gee.csv"
)

INTERACTION_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "height_sex_interaction.csv"
)

MECHANISM_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "semifinal_final_mechanism.csv"
)

FIGURE_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "figures"
    / "semifinal_final_mechanism.png"
)


# ============================================================
# LOAD DATA
# ============================================================

men = pd.read_csv(
    MEN_FILE
)

women = pd.read_csv(
    WOMEN_FILE
)

physical = pd.read_csv(
    PHYSICAL_FILE
)


men["sex"] = "Men"
women["sex"] = "Women"


swims = pd.concat(
    [men, women],
    ignore_index=True
)


if "primary_elite_sample" in swims.columns:

    swims = swims[
        swims["primary_elite_sample"] == True
    ].copy()


physical_small = physical[[
    "swimmer_id",
    "height_cm",
    "weight_kg",
    "bmi"
]].copy()


swims = swims.merge(
    physical_small,
    on="swimmer_id",
    how="left"
)


print("=" * 80)
print("PHYSICAL PERFORMANCE ANALYSIS")
print("=" * 80)

print(
    f"Elite swims: "
    f"{len(swims)}"
)

print(
    f"Unique swimmers: "
    f"{swims['swimmer_id'].nunique()}"
)

print()


# ============================================================
# STEP 1
# ATHLETE-LEVEL CORRELATIONS
# ============================================================

print("=" * 80)
print("STEP 1 - ATHLETE-LEVEL CORRELATIONS")
print("=" * 80)


performance_metrics = [
    "final_time",
    "first_50",
    "second_50",
    "dropoff_percent"
]


if "reaction_time" in swims.columns:
    performance_metrics.append(
        "reaction_time"
    )


athlete_performance = (
    swims
    .groupby(
        [
            "swimmer_id",
            "swimmer_name",
            "sex"
        ],
        as_index=False
    )
    .agg({
        **{
            metric: "mean"
            for metric in performance_metrics
        },
        "height_cm": "first",
        "weight_kg": "first",
        "bmi": "first"
    })
)


correlation_results = []


for sex in [
    "Men",
    "Women"
]:

    print()
    print(
        sex.upper()
    )
    print("-" * 80)

    sex_data = athlete_performance[
        athlete_performance[
            "sex"
        ] == sex
    ].copy()

    for physical_variable in [
        "height_cm",
        "weight_kg"
    ]:

        print()
        print(
            physical_variable.upper()
        )

        for performance_variable in (
            performance_metrics
        ):

            subset = sex_data[[
                physical_variable,
                performance_variable
            ]].dropna()

            if len(subset) < 5:
                continue

            pearson_r, pearson_p = pearsonr(
                subset[
                    physical_variable
                ],
                subset[
                    performance_variable
                ]
            )

            spearman_r, spearman_p = (
                spearmanr(
                    subset[
                        physical_variable
                    ],
                    subset[
                        performance_variable
                    ]
                )
            )

            print(
                f"{performance_variable:20s} "
                f"n={len(subset):3d}  "
                f"r={pearson_r:+.3f}  "
                f"p={pearson_p:.4f}"
            )

            correlation_results.append({
                "sex":
                    sex,

                "physical_variable":
                    physical_variable,

                "performance_variable":
                    performance_variable,

                "n":
                    len(subset),

                "pearson_r":
                    pearson_r,

                "pearson_p":
                    pearson_p,

                "spearman_r":
                    spearman_r,

                "spearman_p":
                    spearman_p
            })


correlation_df = pd.DataFrame(
    correlation_results
)


correlation_df.to_csv(
    CORRELATION_OUTPUT,
    index=False
)


print()


# ============================================================
# STEP 2
# HEIGHT MISSINGNESS CHECK
# ============================================================

print("=" * 80)
print("STEP 2 - HEIGHT MISSINGNESS CHECK")
print("=" * 80)


missingness = (
    swims
    .groupby(
        [
            "swimmer_id",
            "swimmer_name",
            "sex"
        ],
        as_index=False
    )
    .agg(
        final_time=(
            "final_time",
            "mean"
        ),

        first_50=(
            "first_50",
            "mean"
        ),

        second_50=(
            "second_50",
            "mean"
        ),

        dropoff_percent=(
            "dropoff_percent",
            "mean"
        ),

        competition_year=(
            "competition_year",
            "mean"
        ),

        height_cm=(
            "height_cm",
            "first"
        )
    )
)


missingness[
    "height_available"
] = missingness[
    "height_cm"
].notna()


for sex in [
    "Men",
    "Women"
]:

    print()
    print(
        sex.upper()
    )
    print("-" * 80)

    data = missingness[
        missingness[
            "sex"
        ] == sex
    ]

    print(
        f"Height available: "
        f"{data['height_available'].sum()}"
    )

    print(
        f"Height missing: "
        f"{(~data['height_available']).sum()}"
    )

    for variable in [
        "final_time",
        "first_50",
        "second_50",
        "dropoff_percent",
        "competition_year"
    ]:

        available = (
            data.loc[
                data[
                    "height_available"
                ],
                variable
            ]
            .dropna()
        )

        missing = (
            data.loc[
                ~data[
                    "height_available"
                ],
                variable
            ]
            .dropna()
        )

        test = ttest_ind(
            available,
            missing,
            equal_var=False
        )

        print(
            f"{variable:20s} "
            f"with={available.mean():.3f}  "
            f"without={missing.mean():.3f}  "
            f"p={test.pvalue:.4f}"
        )


print()


# ============================================================
# STEP 3
# SEX-SPECIFIC GEE HEIGHT MODELS
# ============================================================

print("=" * 80)
print("STEP 3 - SEX-SPECIFIC GEE HEIGHT MODELS")
print("=" * 80)


swims[
    "height_centered"
] = (
    swims[
        "height_cm"
    ]
    -
    swims.groupby(
        "sex"
    )[
        "height_cm"
    ].transform(
        "mean"
    )
)


swims[
    "year_centered_by_sex"
] = (
    swims[
        "competition_year"
    ]
    -
    swims.groupby(
        "sex"
    )[
        "competition_year"
    ].transform(
        "mean"
    )
)


gee_results = []


for sex in [
    "Men",
    "Women"
]:

    print()
    print(
        sex.upper()
    )
    print("-" * 80)

    sex_data = swims[
        swims[
            "sex"
        ] == sex
    ].copy()

    for outcome in [
        "final_time",
        "first_50",
        "second_50",
        "dropoff_percent"
    ]:

        required = [
            outcome,
            "height_centered",
            "year_centered_by_sex",
            "age",
            "reaction_time",
            "race_round",
            "swimmer_id"
        ]

        model_data = (
            sex_data[
                required
            ]
            .dropna()
            .copy()
        )

        formula = (
            f"{outcome} ~ "
            f"height_centered + "
            f"year_centered_by_sex + "
            f"age + "
            f"reaction_time + "
            f"C(race_round)"
        )

        model = smf.gee(
            formula=formula,
            groups="swimmer_id",
            data=model_data,
            family=(
                sm.families.Gaussian()
            ),
            cov_struct=(
                sm.cov_struct.Exchangeable()
            )
        )

        fit = model.fit()

        coefficient = (
            fit.params[
                "height_centered"
            ]
        )

        se = (
            fit.bse[
                "height_centered"
            ]
        )

        p_value = (
            fit.pvalues[
                "height_centered"
            ]
        )

        ci = (
            fit.conf_int()
            .loc[
                "height_centered"
            ]
        )

        print()
        print(
            f"Outcome: "
            f"{outcome}"
        )

        print(
            f"Swims: "
            f"{len(model_data)}"
        )

        print(
            f"Athletes: "
            f"{model_data['swimmer_id'].nunique()}"
        )

        print(
            f"Height coefficient: "
            f"{coefficient:+.4f}"
        )

        print(
            f"p-value: "
            f"{p_value:.6f}"
        )

        gee_results.append({
            "sex":
                sex,

            "outcome":
                outcome,

            "n_swims":
                len(model_data),

            "n_athletes":
                model_data[
                    "swimmer_id"
                ].nunique(),

            "height_coefficient":
                coefficient,

            "standard_error":
                se,

            "p_value":
                p_value,

            "ci_lower":
                ci.iloc[0],

            "ci_upper":
                ci.iloc[1]
        })


gee_df = pd.DataFrame(
    gee_results
)


gee_df.to_csv(
    GEE_OUTPUT,
    index=False
)


print()


# ============================================================
# STEP 4
# HEIGHT x SEX INTERACTION
# ============================================================

print("=" * 80)
print("STEP 4 - HEIGHT x SEX INTERACTION")
print("=" * 80)


swims[
    "year_centered"
] = (
    swims[
        "competition_year"
    ]
    -
    swims[
        "competition_year"
    ].mean()
)


swims["sex"] = pd.Categorical(
    swims["sex"],
    categories=[
        "Men",
        "Women"
    ]
)


interaction_results = []


for outcome in [
    "final_time",
    "first_50",
    "second_50",
    "dropoff_percent"
]:

    model_data = (
        swims[[
            outcome,
            "height_centered",
            "sex",
            "year_centered",
            "age",
            "reaction_time",
            "race_round",
            "swimmer_id"
        ]]
        .dropna()
        .copy()
    )

    formula = (
        f"{outcome} ~ "
        f"height_centered * C(sex) + "
        f"year_centered + "
        f"age + "
        f"reaction_time + "
        f"C(race_round)"
    )

    model = smf.gee(
        formula=formula,
        groups="swimmer_id",
        data=model_data,
        family=(
            sm.families.Gaussian()
        ),
        cov_struct=(
            sm.cov_struct.Exchangeable()
        )
    )

    fit = model.fit()

    interaction_name = (
        "height_centered:"
        "C(sex)[T.Women]"
    )

    interaction_coef = (
        fit.params[
            interaction_name
        ]
    )

    interaction_se = (
        fit.bse[
            interaction_name
        ]
    )

    interaction_p = (
        fit.pvalues[
            interaction_name
        ]
    )

    interaction_ci = (
        fit.conf_int()
        .loc[
            interaction_name
        ]
    )

    men_effect = (
        fit.params[
            "height_centered"
        ]
    )

    women_effect = (
        men_effect
        +
        interaction_coef
    )

    print()
    print(
        f"Outcome: "
        f"{outcome}"
    )

    print(
        f"Men height effect: "
        f"{men_effect:+.4f}"
    )

    print(
        f"Women height effect: "
        f"{women_effect:+.4f}"
    )

    print(
        f"Interaction p: "
        f"{interaction_p:.6f}"
    )

    interaction_results.append({
        "outcome":
            outcome,

        "n_swims":
            len(model_data),

        "n_athletes":
            model_data[
                "swimmer_id"
            ].nunique(),

        "men_height_effect":
            men_effect,

        "women_height_effect":
            women_effect,

        "interaction_coefficient":
            interaction_coef,

        "interaction_se":
            interaction_se,

        "interaction_p":
            interaction_p,

        "interaction_ci_lower":
            interaction_ci.iloc[0],

        "interaction_ci_upper":
            interaction_ci.iloc[1]
    })


interaction_df = pd.DataFrame(
    interaction_results
)


interaction_df.to_csv(
    INTERACTION_OUTPUT,
    index=False
)


print()


# ============================================================
# STEP 5
# SEMIFINAL vs FINAL MECHANISM
# ============================================================

print("=" * 80)
print("STEP 5 - SEMIFINAL vs FINAL MECHANISM")
print("=" * 80)


mechanism_metrics = [
    "first_50",
    "second_50",
    "final_time",
    "dropoff_seconds",
    "dropoff_percent"
]


mechanism_results = []


for sex in [
    "Men",
    "Women"
]:

    sex_data = swims[
        swims[
            "sex"
        ] == sex
    ].copy()

    sex_data = sex_data[
        sex_data[
            "race_round"
        ].isin(
            [
                "Semifinals",
                "Finals"
            ]
        )
    ].copy()

    paired = sex_data.pivot_table(
        index=[
            "competition_id",
            "swimmer_id",
            "swimmer_name"
        ],
        columns="race_round",
        values=mechanism_metrics,
        aggfunc="first"
    )

    paired = paired.dropna(
        subset=[
            (
                metric,
                round_name
            )
            for metric in mechanism_metrics
            for round_name in [
                "Semifinals",
                "Finals"
            ]
        ]
    ).copy()

    print()
    print(
        sex.upper()
    )
    print("-" * 80)

    print(
        f"Pairs: "
        f"{len(paired)}"
    )

    for metric in mechanism_metrics:

        semi = paired[
            (
                metric,
                "Semifinals"
            )
        ]

        final = paired[
            (
                metric,
                "Finals"
            )
        ]

        difference = (
            final - semi
        )

        t_test = ttest_rel(
            final,
            semi
        )

        try:

            wilcoxon_p = wilcoxon(
                final,
                semi
            ).pvalue

        except ValueError:

            wilcoxon_p = None

        mean_difference = (
            difference.mean()
        )

        sd_difference = (
            difference.std()
        )

        se_difference = (
            sd_difference
            /
            (
                len(
                    difference
                ) ** 0.5
            )
        )

        ci_lower = (
            mean_difference
            -
            1.96
            *
            se_difference
        )

        ci_upper = (
            mean_difference
            +
            1.96
            *
            se_difference
        )

        print(
            f"{metric:20s} "
            f"{mean_difference:+.4f}  "
            f"p={t_test.pvalue:.6f}"
        )

        mechanism_results.append({
            "sex":
                sex,

            "metric":
                metric,

            "n_pairs":
                len(difference),

            "semifinal_mean":
                semi.mean(),

            "final_mean":
                final.mean(),

            "mean_difference":
                mean_difference,

            "median_difference":
                difference.median(),

            "sd_difference":
                sd_difference,

            "ci_lower":
                ci_lower,

            "ci_upper":
                ci_upper,

            "paired_t_p":
                t_test.pvalue,

            "wilcoxon_p":
                wilcoxon_p
        })


mechanism_df = pd.DataFrame(
    mechanism_results
)


mechanism_df.to_csv(
    MECHANISM_OUTPUT,
    index=False
)


print()


# ============================================================
# STEP 6
# SEMIFINAL vs FINAL MECHANISM FIGURE
# ============================================================

print("=" * 80)
print("STEP 6 - CREATE MECHANISM FIGURE")
print("=" * 80)


figure_metrics = [
    "first_50",
    "second_50",
    "final_time"
]


labels = {
    "first_50":
        "First 50 m",

    "second_50":
        "Second 50 m",

    "final_time":
        "Final Time"
}


men_figure = (
    mechanism_df[
        (
            mechanism_df[
                "sex"
            ] == "Men"
        )
        &
        (
            mechanism_df[
                "metric"
            ].isin(
                figure_metrics
            )
        )
    ]
    .set_index(
        "metric"
    )
    .loc[
        figure_metrics
    ]
)


women_figure = (
    mechanism_df[
        (
            mechanism_df[
                "sex"
            ] == "Women"
        )
        &
        (
            mechanism_df[
                "metric"
            ].isin(
                figure_metrics
            )
        )
    ]
    .set_index(
        "metric"
    )
    .loc[
        figure_metrics
    ]
)


x = list(
    range(
        len(
            figure_metrics
        )
    )
)

width = 0.35


fig, ax = plt.subplots(
    figsize=(
        10,
        6
    )
)


men_positions = [
    value
    - width / 2
    for value in x
]

women_positions = [
    value
    + width / 2
    for value in x
]


ax.bar(
    men_positions,
    men_figure[
        "mean_difference"
    ],
    width,
    label="Men"
)


ax.bar(
    women_positions,
    women_figure[
        "mean_difference"
    ],
    width,
    label="Women"
)


ax.axhline(
    0,
    linewidth=1
)


ax.set_xticks(
    x
)


ax.set_xticklabels(
    [
        labels[
            metric
        ]
        for metric in figure_metrics
    ],
    fontsize=12
)


ax.set_ylabel(
    "Final minus semifinal time (seconds)",
    fontsize=12
)


ax.set_title(
    "How Race Strategy Changes from Semifinal to Final",
    fontsize=16
)


ax.legend(
    fontsize=11
)


ax.set_ylim(
    -0.19,
    0.085
)


for positions, values in [
    (
        men_positions,
        men_figure[
            "mean_difference"
        ]
    ),
    (
        women_positions,
        women_figure[
            "mean_difference"
        ]
    )
]:

    for position, value in zip(
        positions,
        values
    ):

        if value >= 0:

            y_position = (
                value
                + 0.006
            )

            vertical_alignment = (
                "bottom"
            )

        else:

            y_position = (
                value
                - 0.010
            )

            vertical_alignment = (
                "top"
            )

        ax.text(
            position,
            y_position,
            f"{value:+.3f}",
            ha="center",
            va=vertical_alignment,
            fontsize=14,
            fontweight="bold",
            bbox={
                "facecolor":
                    "white",

                "alpha":
                    0.9,

                "edgecolor":
                    "none",

                "pad":
                    3
            }
        )


ax.tick_params(
    axis="y",
    labelsize=11
)


plt.tight_layout()


plt.savefig(
    FIGURE_OUTPUT,
    dpi=300,
    bbox_inches="tight"
)


plt.close()


print(
    f"Figure saved to:"
)

print(
    FIGURE_OUTPUT
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)

print()

print(
    "Saved tables:"
)

print(
    CORRELATION_OUTPUT
)

print(
    GEE_OUTPUT
)

print(
    INTERACTION_OUTPUT
)

print(
    MECHANISM_OUTPUT
)

print()

print(
    "Saved figure:"
)

print(
    FIGURE_OUTPUT
)
