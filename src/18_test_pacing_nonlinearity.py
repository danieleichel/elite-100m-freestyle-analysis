import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
from pathlib import Path


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


def analyze_pacing(file_path, label):

    df = pd.read_csv(file_path)

    sample = df[
        df["primary_elite_sample"] == True
    ].copy()

    # Center year to make coefficients easier to interpret
    sample["year_centered"] = (
        sample["competition_year"]
        - sample["competition_year"].mean()
    )

    # Square term for nonlinear pacing relationship
    sample["dropoff_squared"] = (
        sample["dropoff_percent"] ** 2
    )

    # Linear pacing model
    linear_model = smf.ols(
        """
        final_time ~
        dropoff_percent +
        reaction_time +
        age +
        year_centered +
        C(race_round)
        """,
        data=sample
    ).fit()

    # Quadratic pacing model
    quadratic_model = smf.ols(
        """
        final_time ~
        dropoff_percent +
        dropoff_squared +
        reaction_time +
        age +
        year_centered +
        C(race_round)
        """,
        data=sample
    ).fit()

    print()
    print("=" * 80)
    print(label)
    print("=" * 80)

    print("\nLINEAR MODEL")
    print(f"R-squared: {linear_model.rsquared:.4f}")
    print(f"Adjusted R-squared: {linear_model.rsquared_adj:.4f}")
    print(f"AIC: {linear_model.aic:.2f}")
    print(f"BIC: {linear_model.bic:.2f}")

    print("\nQUADRATIC MODEL")
    print(f"R-squared: {quadratic_model.rsquared:.4f}")
    print(f"Adjusted R-squared: {quadratic_model.rsquared_adj:.4f}")
    print(f"AIC: {quadratic_model.aic:.2f}")
    print(f"BIC: {quadratic_model.bic:.2f}")

    print("\nQUADRATIC PACING COEFFICIENTS")

    print(
        quadratic_model.summary2().tables[1]
        .loc[
            [
                "dropoff_percent",
                "dropoff_squared"
            ]
        ]
    )

    print("\nNESTED MODEL COMPARISON")

    comparison = anova_lm(
        linear_model,
        quadratic_model
    )

    print(comparison)

    # Estimate turning point
    beta1 = quadratic_model.params["dropoff_percent"]
    beta2 = quadratic_model.params["dropoff_squared"]

    if beta2 != 0:

        optimal_dropoff = (
            -beta1
            / (2 * beta2)
        )

        print(
            f"\nEstimated quadratic turning point: "
            f"{optimal_dropoff:.2f}%"
        )


analyze_pacing(
    MEN_FILE,
    "MEN - PACING NONLINEARITY"
)

analyze_pacing(
    WOMEN_FILE,
    "WOMEN - PACING NONLINEARITY"
)
