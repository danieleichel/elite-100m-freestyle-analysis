import pandas as pd
import statsmodels.formula.api as smf
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


def fit_mixed_model(file_path, label):

    df = pd.read_csv(file_path)

    sample = df[
        df["primary_elite_sample"] == True
    ].copy()

    sample["year_centered"] = (
        sample["competition_year"]
        - sample["competition_year"].mean()
    )

    sample = sample.dropna(
        subset=[
            "dropoff_percent",
            "reaction_time",
            "age",
            "swimmer_id",
            "race_round"
        ]
    )

    model = smf.mixedlm(
        """
        dropoff_percent ~
        year_centered +
        reaction_time +
        age +
        C(race_round)
        """,
        data=sample,
        groups=sample["swimmer_id"]
    )

    result = model.fit(
        method="lbfgs",
        reml=False
    )

    print()
    print("=" * 80)
    print(label)
    print("=" * 80)

    print(result.summary())

    print()
    print("YEAR EFFECT:")

    beta = result.params["year_centered"]
    p_value = result.pvalues["year_centered"]

    print(
        f"Estimated annual change: "
        f"{beta:.4f} percentage points"
    )

    print(
        f"P-value: "
        f"{p_value:.6f}"
    )

    print()
    print("RANDOM INTERCEPT VARIANCE:")

    print(result.cov_re)


fit_mixed_model(
    MEN_FILE,
    "MEN - MIXED EFFECTS PACING MODEL"
)

fit_mixed_model(
    WOMEN_FILE,
    "WOMEN - MIXED EFFECTS PACING MODEL"
)
