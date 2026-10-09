import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from pathlib import Path


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

OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "pacing_models_summary.csv"
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


# ============================================================
# PREPARE VARIABLES
# ============================================================

swims["year_centered"] = (
    swims["competition_year"]
    - swims.groupby("sex")[
        "competition_year"
    ].transform("mean")
)


results = []


# ============================================================
# RUN MODELS BY SEX
# ============================================================

for sex in [
    "Men",
    "Women"
]:

    print()
    print("=" * 80)
    print(sex.upper())
    print("=" * 80)

    data = swims[
        swims["sex"] == sex
    ].copy()

    # ========================================================
    # MODEL 1 - NONLINEARITY
    # ========================================================

    print()
    print("MODEL 1 - NONLINEARITY")
    print("-" * 80)

    nonlinear_data = (
        data[[
            "final_time",
            "dropoff_percent",
            "year_centered",
            "age",
            "reaction_time",
            "race_round"
        ]]
        .dropna()
        .copy()
    )

    nonlinear_data[
        "dropoff_squared"
    ] = (
        nonlinear_data[
            "dropoff_percent"
        ] ** 2
    )

    linear_formula = (
        "final_time ~ "
        "dropoff_percent + "
        "year_centered + "
        "age + "
        "reaction_time + "
        "C(race_round)"
    )

    quadratic_formula = (
        "final_time ~ "
        "dropoff_percent + "
        "dropoff_squared + "
        "year_centered + "
        "age + "
        "reaction_time + "
        "C(race_round)"
    )

    linear_fit = smf.ols(
        linear_formula,
        data=nonlinear_data
    ).fit()

    quadratic_fit = smf.ols(
        quadratic_formula,
        data=nonlinear_data
    ).fit()

    quad_p = (
        quadratic_fit.pvalues[
            "dropoff_squared"
        ]
    )

    nested_test = (
        quadratic_fit.compare_f_test(
            linear_fit
        )
    )

    nested_p = (
        nested_test[1]
    )

    print(
        f"Linear R2: "
        f"{linear_fit.rsquared:.4f}"
    )

    print(
        f"Quadratic R2: "
        f"{quadratic_fit.rsquared:.4f}"
    )

    print(
        f"Linear adjusted R2: "
        f"{linear_fit.rsquared_adj:.4f}"
    )

    print(
        f"Quadratic adjusted R2: "
        f"{quadratic_fit.rsquared_adj:.4f}"
    )

    print(
        f"Linear AIC: "
        f"{linear_fit.aic:.2f}"
    )

    print(
        f"Quadratic AIC: "
        f"{quadratic_fit.aic:.2f}"
    )

    print(
        f"Linear BIC: "
        f"{linear_fit.bic:.2f}"
    )

    print(
        f"Quadratic BIC: "
        f"{quadratic_fit.bic:.2f}"
    )

    print(
        f"Dropoff coefficient p: "
        f"{quadratic_fit.pvalues['dropoff_percent']:.6f}"
    )

    print(
        f"Quadratic term p: "
        f"{quad_p:.6f}"
    )

    print(
        f"Nested-model p: "
        f"{nested_p:.6f}"
    )

    results.append({
        "sex":
            sex,

        "model":
            "nonlinearity",

        "parameter":
            "dropoff_squared",

        "estimate":
            quadratic_fit.params[
                "dropoff_squared"
            ],

        "standard_error":
            quadratic_fit.bse[
                "dropoff_squared"
            ],

        "p_value":
            quad_p
    })

    # ========================================================
    # COMMON DATA FOR TREND MODELS
    # ========================================================

    trend_required = [
        "dropoff_percent",
        "year_centered",
        "age",
        "reaction_time",
        "race_round",
        "swimmer_id"
    ]

    model_data = (
        data[
            trend_required
        ]
        .dropna()
        .copy()
    )

    trend_formula = (
        "dropoff_percent ~ "
        "year_centered + "
        "age + "
        "reaction_time + "
        "C(race_round)"
    )

    # ========================================================
    # MODEL 2 - SIMPLE OLS TIME TREND
    # ========================================================

    print()
    print("MODEL 2 - OLS TIME TREND")
    print("-" * 80)

    trend_fit = smf.ols(
        trend_formula,
        data=model_data
    ).fit()

    year_coef = (
        trend_fit.params[
            "year_centered"
        ]
    )

    year_p = (
        trend_fit.pvalues[
            "year_centered"
        ]
    )

    year_ci = (
        trend_fit.conf_int()
        .loc[
            "year_centered"
        ]
    )

    print(
        f"R2: "
        f"{trend_fit.rsquared:.4f}"
    )

    print(
        f"Year coefficient: "
        f"{year_coef:+.4f}"
    )

    print(
        f"SE: "
        f"{trend_fit.bse['year_centered']:.4f}"
    )

    print(
        f"p-value: "
        f"{year_p:.6f}"
    )

    print(
        f"95% CI: "
        f"[{year_ci.iloc[0]:+.4f}, "
        f"{year_ci.iloc[1]:+.4f}]"
    )

    results.append({
        "sex":
            sex,

        "model":
            "ols_trend",

        "parameter":
            "year_centered",

        "estimate":
            year_coef,

        "standard_error":
            trend_fit.bse[
                "year_centered"
            ],

        "p_value":
            year_p
    })

    # ========================================================
    # MODEL 3 - MIXED EFFECTS
    # ========================================================

    print()
    print("MODEL 3 - MIXED EFFECTS")
    print("-" * 80)

    mixed_model = smf.mixedlm(
        trend_formula,
        data=model_data,
        groups=model_data[
            "swimmer_id"
        ]
    )

    mixed_fit = mixed_model.fit(
        reml=False,
        method="lbfgs"
    )

    mixed_year = (
        mixed_fit.params[
            "year_centered"
        ]
    )

    mixed_p = (
        mixed_fit.pvalues[
            "year_centered"
        ]
    )

    mixed_ci = (
        mixed_fit.conf_int()
        .loc[
            "year_centered"
        ]
    )

    print(
        f"Year coefficient: "
        f"{mixed_year:+.4f}"
    )

    print(
        f"SE: "
        f"{mixed_fit.bse['year_centered']:.4f}"
    )

    print(
        f"p-value: "
        f"{mixed_p:.6f}"
    )

    print(
        f"95% CI: "
        f"[{mixed_ci.iloc[0]:+.4f}, "
        f"{mixed_ci.iloc[1]:+.4f}]"
    )

    if "Group Var" in mixed_fit.params.index:

        print(
            f"Group variance: "
            f"{mixed_fit.params['Group Var']:.4f}"
        )

    results.append({
        "sex":
            sex,

        "model":
            "mixedlm",

        "parameter":
            "year_centered",

        "estimate":
            mixed_year,

        "standard_error":
            mixed_fit.bse[
                "year_centered"
            ],

        "p_value":
            mixed_p
    })

    # ========================================================
    # MODEL 4 - CLUSTER ROBUST OLS
    # ========================================================

    print()
    print("MODEL 4 - CLUSTER ROBUST OLS")
    print("-" * 80)

    cluster_fit = smf.ols(
        trend_formula,
        data=model_data
    ).fit(
        cov_type="cluster",
        cov_kwds={
            "groups":
                model_data[
                    "swimmer_id"
                ]
        }
    )

    cluster_year = (
        cluster_fit.params[
            "year_centered"
        ]
    )

    cluster_p = (
        cluster_fit.pvalues[
            "year_centered"
        ]
    )

    cluster_ci = (
        cluster_fit.conf_int()
        .loc[
            "year_centered"
        ]
    )

    print(
        f"Year coefficient: "
        f"{cluster_year:+.4f}"
    )

    print(
        f"Cluster SE: "
        f"{cluster_fit.bse['year_centered']:.4f}"
    )

    print(
        f"p-value: "
        f"{cluster_p:.6f}"
    )

    print(
        f"95% CI: "
        f"[{cluster_ci.iloc[0]:+.4f}, "
        f"{cluster_ci.iloc[1]:+.4f}]"
    )

    results.append({
        "sex":
            sex,

        "model":
            "cluster_robust_ols",

        "parameter":
            "year_centered",

        "estimate":
            cluster_year,

        "standard_error":
            cluster_fit.bse[
                "year_centered"
            ],

        "p_value":
            cluster_p
    })

    # ========================================================
    # MODEL 5 - GEE
    # ========================================================

    print()
    print("MODEL 5 - GEE")
    print("-" * 80)

    gee_model = smf.gee(
        formula=trend_formula,
        groups="swimmer_id",
        data=model_data,
        family=(
            sm.families.Gaussian()
        ),
        cov_struct=(
            sm.cov_struct.Exchangeable()
        )
    )

    gee_fit = (
        gee_model.fit()
    )

    gee_year = (
        gee_fit.params[
            "year_centered"
        ]
    )

    gee_p = (
        gee_fit.pvalues[
            "year_centered"
        ]
    )

    gee_ci = (
        gee_fit.conf_int()
        .loc[
            "year_centered"
        ]
    )

    dep = getattr(
        gee_fit.cov_struct,
        "dep_params",
        None
    )

    print(
        f"Year coefficient: "
        f"{gee_year:+.4f}"
    )

    print(
        f"Robust SE: "
        f"{gee_fit.bse['year_centered']:.4f}"
    )

    print(
        f"p-value: "
        f"{gee_p:.6f}"
    )

    print(
        f"95% CI: "
        f"[{gee_ci.iloc[0]:+.4f}, "
        f"{gee_ci.iloc[1]:+.4f}]"
    )

    print(
        f"Estimated within-swimmer correlation: "
        f"{dep}"
    )

    results.append({
        "sex":
            sex,

        "model":
            "gee",

        "parameter":
            "year_centered",

        "estimate":
            gee_year,

        "standard_error":
            gee_fit.bse[
                "year_centered"
            ],

        "p_value":
            gee_p
    })


# ============================================================
# SAVE SUMMARY
# ============================================================

results_df = pd.DataFrame(
    results
)


results_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("=" * 80)
print("PACING MODEL ANALYSIS COMPLETE")
print("=" * 80)

print(
    "Saved to:"
)

print(
    OUTPUT_FILE
)
