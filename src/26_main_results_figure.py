import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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

FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def get_paired_summary(file_path, sex_label):

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
        subset=["Semifinals", "Finals"]
    )

    results = []

    for round_name in ["Semifinals", "Finals"]:

        values = paired[round_name]

        n = len(values)
        mean = values.mean()
        sd = values.std(ddof=1)
        se = sd / np.sqrt(n)

        t_critical = t.ppf(
            0.975,
            df=n - 1
        )

        margin = t_critical * se

        results.append({
            "sex": sex_label,
            "round": round_name,
            "n": n,
            "mean": mean,
            "ci_lower": mean - margin,
            "ci_upper": mean + margin
        })

    return pd.DataFrame(results)


men_summary = get_paired_summary(
    MEN_FILE,
    "Men"
)

women_summary = get_paired_summary(
    WOMEN_FILE,
    "Women"
)

summary = pd.concat(
    [men_summary, women_summary],
    ignore_index=True
)


print()
print("SUMMARY DATA")
print("=" * 70)
print(
    summary
    .round(3)
    .to_string(index=False)
)


fig, ax = plt.subplots(figsize=(10, 6))

x_positions = {
    ("Men", "Semifinals"): 0,
    ("Men", "Finals"): 1,
    ("Women", "Semifinals"): 3,
    ("Women", "Finals"): 4
}

for _, row in summary.iterrows():

    x = x_positions[
        (row["sex"], row["round"])
    ]

    lower_error = (
        row["mean"]
        - row["ci_lower"]
    )

    upper_error = (
        row["ci_upper"]
        - row["mean"]
    )

    ax.errorbar(
        x,
        row["mean"],
        yerr=np.array(
            [[lower_error], [upper_error]]
        ),
        fmt="o",
        markersize=9,
        capsize=6,
        linewidth=2
    )

    ax.text(
        x,
        row["mean"] + 0.35,
        f"{row['mean']:.2f}%",
        ha="center",
        fontsize=11
    )


# Connect semifinal and final means
ax.plot(
    [0, 1],
    [
        men_summary.loc[
            men_summary["round"] == "Semifinals",
            "mean"
        ].iloc[0],
        men_summary.loc[
            men_summary["round"] == "Finals",
            "mean"
        ].iloc[0]
    ],
    linewidth=1.5
)

ax.plot(
    [3, 4],
    [
        women_summary.loc[
            women_summary["round"] == "Semifinals",
            "mean"
        ].iloc[0],
        women_summary.loc[
            women_summary["round"] == "Finals",
            "mean"
        ].iloc[0]
    ],
    linewidth=1.5
)


ax.set_xticks(
    [0, 1, 3, 4]
)

ax.set_xticklabels(
    [
        "Men\nSemifinal",
        "Men\nFinal",
        "Women\nSemifinal",
        "Women\nFinal"
    ]
)

ax.set_ylabel(
    "Mean Second-Half Dropoff (%)"
)

ax.set_title(
    "Elite 100m Freestyle Pacing Changes from Semifinal to Final"
)

ax.text(
    0.5,
    10.9,
    "+0.82 pp",
    ha="center",
    fontsize=11
)

ax.text(
    3.5,
    9.25,
    "+0.91 pp",
    ha="center",
    fontsize=11
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()

output_path = (
    FIGURES_DIR
    / "main_semifinal_final_result.png"
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print()
print(f"Saved main figure: {output_path}")
