import pandas as pd
from scipy.stats import ttest_rel, wilcoxon
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


def paired_analysis(file_path, label):

    df = pd.read_csv(file_path)

    sample = df[
        df["primary_elite_sample"] == True
    ].copy()

    # Keep only semifinal and final swims
    sample = sample[
        sample["race_round"].isin(
            ["Semifinals", "Finals"]
        )
    ]

    # Build one row per swimmer-meet
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

    # Keep swimmers with both semifinal and final
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

    print()
    print("=" * 80)
    print(label)
    print("=" * 80)

    print(f"Paired swimmers: {len(paired)}")

    print()
    print("SEMIFINAL DROPOFF:")
    print(
        paired["Semifinals"]
        .describe()
        .round(3)
    )

    print()
    print("FINAL DROPOFF:")
    print(
        paired["Finals"]
        .describe()
        .round(3)
    )

    print()
    print("FINAL - SEMIFINAL DIFFERENCE:")
    print(
        paired["difference"]
        .describe()
        .round(3)
    )

    # Paired t-test
    t_result = ttest_rel(
        paired["Finals"],
        paired["Semifinals"]
    )

    print()
    print("PAIRED T-TEST:")
    print(
        f"t = {t_result.statistic:.4f}"
    )
    print(
        f"p = {t_result.pvalue:.6f}"
    )

    # Wilcoxon signed-rank test
    wilcox_result = wilcoxon(
        paired["Finals"],
        paired["Semifinals"],
        zero_method="wilcox"
    )

    print()
    print("WILCOXON SIGNED-RANK TEST:")
    print(
        f"statistic = {wilcox_result.statistic:.4f}"
    )
    print(
        f"p = {wilcox_result.pvalue:.6f}"
    )

    print()
    print("FIRST 10 PAIRED OBSERVATIONS:")

    print(
        paired[
            [
                "competition_id",
                "swimmer_name",
                "Semifinals",
                "Finals",
                "difference"
            ]
        ]
        .head(10)
        .round(3)
        .to_string(index=False)
    )


paired_analysis(
    MEN_FILE,
    "MEN - SEMIFINAL VS FINAL PACING"
)

paired_analysis(
    WOMEN_FILE,
    "WOMEN - SEMIFINAL VS FINAL PACING"
)
