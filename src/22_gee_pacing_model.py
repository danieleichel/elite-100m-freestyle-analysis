import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.genmod.cov_struct import Exchangeable
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


def fit_gee(file_path, label):

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
            "race_round",
            "swimmer_id"
        ]
    )

    model = smf.gee(
        """
        dropoff_percent ~
        year_centered +
        reaction_time +
        age +
        C(race_round)
        """,
        groups="swimmer_id",
        data=sample,
        family=sm.families.Gaussian(),
        cov_struct=Exchangeable()
    )

    result = model.fit()

    print()
    print("=" * 80)
    print(label)
    print("=" * 80)

    print(result.summary())

    print()
    print("KEY RESULTS:")

    for variable in [
        "year_centered",
        "reaction_time",
        "age",
        "C(race_round)[T.Semifinals]"
    ]:

        print(
            f"{variable}: "
            f"coef = {result.params[variable]:.4f}, "
            f"SE = {result.bse[variable]:.4f}, "
            f"p = {result.pvalues[variable]:.6f}"
        )

    print()
    print(
        "Estimated within-swimmer correlation:",
        result.cov_struct.dep_params
    )


fit_gee(
    MEN_FILE,
    "MEN - GEE PACING MODEL"
)

fit_gee(
    WOMEN_FILE,
    "WOMEN - GEE PACING MODEL"
)
