import pandas as pd
import matplotlib.pyplot as plt
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


def prepare_paired_data(file_path):
    df = pd.read_csv(file_path)

    sample = df[df["primary_elite_sample"] == True].copy()

    sample = sample[
        sample["race_round"].isin(["Semifinals", "Finals"])
    ]

    paired = sample.pivot_table(
        index=["competition_id", "swimmer_id", "swimmer_name"],
        columns="race_round",
        values="dropoff_percent",
        aggfunc="mean"
    ).reset_index()

    paired = paired.dropna(subset=["Semifinals", "Finals"])
    paired["difference"] = paired["Finals"] - paired["Semifinals"]

    return paired


def plot_paired_lines(paired_df, label, filename):
    paired_df = paired_df.sort_values("difference").reset_index(drop=True)

    plt.figure(figsize=(10, 6))

    for _, row in paired_df.iterrows():
        plt.plot(
            [0, 1],
            [row["Semifinals"], row["Finals"]],
            alpha=0.25,
            linewidth=1
        )

    semifinal_mean = paired_df["Semifinals"].mean()
    final_mean = paired_df["Finals"].mean()

    plt.plot(
        [0, 1],
        [semifinal_mean, final_mean],
        marker="o",
        linewidth=3,
        label="Mean dropoff"
    )

    plt.xticks([0, 1], ["Semifinal", "Final"])
    plt.ylabel("Dropoff Percent")
    plt.title(f"{label}: Paired Pacing Dropoff\nSemifinal vs Final")
    plt.legend()
    plt.tight_layout()

    output_path = FIGURES_DIR / filename
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")


def plot_difference_histogram(paired_df, label, filename):
    plt.figure(figsize=(10, 6))

    plt.hist(paired_df["difference"], bins=20, edgecolor="black")
    plt.axvline(0, linestyle="--", linewidth=2, label="No change")
    plt.axvline(
        paired_df["difference"].mean(),
        linestyle="-",
        linewidth=2,
        label=f"Mean = {paired_df['difference'].mean():.3f}"
    )

    plt.xlabel("Final - Semifinal Dropoff Percent")
    plt.ylabel("Number of Swims")
    plt.title(f"{label}: Distribution of Paired Difference")
    plt.legend()
    plt.tight_layout()

    output_path = FIGURES_DIR / filename
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")


def run_visualization(file_path, label, paired_filename, hist_filename):
    paired_df = prepare_paired_data(file_path)

    print(f"\n{label}")
    print(f"Paired swimmers: {len(paired_df)}")
    print(f"Mean semifinal dropoff: {paired_df['Semifinals'].mean():.3f}")
    print(f"Mean final dropoff: {paired_df['Finals'].mean():.3f}")
    print(f"Mean difference: {paired_df['difference'].mean():.3f}")

    plot_paired_lines(
        paired_df,
        label,
        paired_filename
    )

    plot_difference_histogram(
        paired_df,
        label,
        hist_filename
    )


run_visualization(
    MEN_FILE,
    "Men",
    "men_paired_semifinal_final.png",
    "men_difference_distribution.png"
)

run_visualization(
    WOMEN_FILE,
    "Women",
    "women_paired_semifinal_final.png",
    "women_difference_distribution.png"
)
