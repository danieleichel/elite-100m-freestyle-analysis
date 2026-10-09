
import pandas as pd
import numpy as np
from scipy.stats import t
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


def paired_effect_analysis(file_path, label):

    df = pd.read_csv(file_path)

    sample = df[
        df["primary_elite_sample"] == True
    ].copy()

    paired = sample.pivot_table(
        index=[
            "competition_id",
            "swimmer_id",
            "swimmer_name"
        ],
        columns="race_round",
        values="dropoff_percent",
        aggfunc="mean"
    ).reset_index()

    paired = paired.dropna(
        subset=[
            "Semifinals",
            "Finals"
        ]
    )

    paired["difference"] = (
        paired["Finals"]
        - paired["Semifinals"]
    )

    differences = paired["difference"]

    n = len(differences)

    mean_diff = differences.mean()
    median_diff = differences.median()
    sd_diff = differences.std(ddof=1)

    se_diff = sd_diff / np.sqrt(n)

    alpha = 0.05
    t_critical = t.ppf(
        1 - alpha / 2,
        df=n - 1
    )

    ci_lower = (
        mean_diff
        - t_critical * se_diff
    )

    ci_upper = (
        mean_diff
        + t_critical * se_diff
    )

    # Cohen's dz for paired samples
    cohens_dz = (
        mean_diff
        / sd_diff
    )

    # Percentage showing greater dropoff in final
    increased = (
        differences > 0
    ).mean() * 100

    decreased = (
        differences < 0
    ).mean() * 100

    unchanged = (
        differences == 0
    ).mean() * 100

    print()
    print("=" * 80)
    print(label)
    print("=" * 80)

    print(f"Paired swimmers: {n}")

    print()
    print(
        f"Mean paired difference: "
        f"{mean_diff:.3f} percentage points"
    )

    print(
        f"Median paired difference: "
        f"{median_diff:.3f} percentage points"
    )

    print(
        f"95% CI: "
        f"[{ci_lower:.3f}, {ci_upper:.3f}]"
    )

    print(
        f"Cohen's dz: "
        f"{cohens_dz:.3f}"
    )

    print()
    print(
        f"Greater dropoff in final: "
        f"{increased:.1f}%"
    )

    print(
        f"Lower dropoff in final: "
        f"{decreased:.1f}%"
    )

    print(
        f"No change: "
        f"{unchanged:.1f}%"
    )


paired_effect_analysis(
    MEN_FILE,
    "MEN - PAIRED EFFECT SIZE"
)

paired_effect_analysis(
    WOMEN_FILE,
    "WOMEN - PAIRED EFFECT SIZE"
)
