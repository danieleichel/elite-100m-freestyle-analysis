import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from scipy.stats import ttest_rel, wilcoxon


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

TABLE_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "semifinal_final_summary.csv"
)

BOOTSTRAP_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "semifinal_final_bootstrap.csv"
)

FIGURE_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "figures"
)


# ============================================================
# SETTINGS
# ============================================================

BOOTSTRAP_REPS = 10000
RANDOM_SEED = 42


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def build_pairs(file_path):

    df = pd.read_csv(
        file_path
    )

    if "primary_elite_sample" in df.columns:

        df = df[
            df["primary_elite_sample"] == True
        ].copy()

    df = df[
        df["race_round"].isin(
            [
                "Semifinals",
                "Finals"
            ]
        )
    ].copy()

    paired = df.pivot_table(
        index=[
            "competition_id",
            "swimmer_id",
            "swimmer_name"
        ],
        columns="race_round",
        values="dropoff_percent",
        aggfunc="first"
    ).dropna()

    paired = paired.rename(
        columns={
            "Semifinals":
                "semifinal_dropoff",

            "Finals":
                "final_dropoff"
        }
    )

    paired[
        "difference"
    ] = (
        paired[
            "final_dropoff"
        ]
        -
        paired[
            "semifinal_dropoff"
        ]
    )

    return paired.reset_index()


def bootstrap_mean_difference(
    differences,
    reps=10000,
    seed=42
):

    rng = np.random.default_rng(
        seed
    )

    differences = np.asarray(
        differences
    )

    n = len(
        differences
    )

    bootstrap_means = np.empty(
        reps
    )

    for i in range(
        reps
    ):

        sample = rng.choice(
            differences,
            size=n,
            replace=True
        )

        bootstrap_means[i] = (
            sample.mean()
        )

    ci_lower = np.percentile(
        bootstrap_means,
        2.5
    )

    ci_upper = np.percentile(
        bootstrap_means,
        97.5
    )

    return (
        bootstrap_means,
        ci_lower,
        ci_upper
    )


def analyze_sex(
    file_path,
    sex_label
):

    paired = build_pairs(
        file_path
    )

    semi = paired[
        "semifinal_dropoff"
    ]

    final = paired[
        "final_dropoff"
    ]

    diff = paired[
        "difference"
    ]

    n = len(
        diff
    )

    # --------------------------------------------------------
    # Classical inference
    # --------------------------------------------------------

    t_test = ttest_rel(
        final,
        semi
    )

    wilcoxon_test = wilcoxon(
        final,
        semi
    )

    mean_diff = (
        diff.mean()
    )

    median_diff = (
        diff.median()
    )

    sd_diff = (
        diff.std(
            ddof=1
        )
    )

    se_diff = (
        sd_diff
        /
        np.sqrt(
            n
        )
    )

    ci_lower = (
        mean_diff
        -
        1.96
        *
        se_diff
    )

    ci_upper = (
        mean_diff
        +
        1.96
        *
        se_diff
    )

    cohens_dz = (
        mean_diff
        /
        sd_diff
    )

    greater_percent = (
        (
            diff > 0
        ).mean()
        *
        100
    )

    lower_percent = (
        (
            diff < 0
        ).mean()
        *
        100
    )

    # --------------------------------------------------------
    # Bootstrap
    # --------------------------------------------------------

    (
        bootstrap_means,
        bootstrap_ci_lower,
        bootstrap_ci_upper
    ) = bootstrap_mean_difference(
        diff,
        reps=BOOTSTRAP_REPS,
        seed=RANDOM_SEED
    )

    bootstrap_se = (
        bootstrap_means.std(
            ddof=1
        )
    )

    bootstrap_positive = (
        bootstrap_means
        > 0
    ).mean()

    # --------------------------------------------------------
    # Print
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print(
        sex_label.upper()
    )
    print("=" * 80)

    print(
        f"Paired observations: "
        f"{n}"
    )

    print()

    print(
        f"Semifinal mean: "
        f"{semi.mean():.4f}%"
    )

    print(
        f"Final mean: "
        f"{final.mean():.4f}%"
    )

    print()

    print(
        f"Mean difference: "
        f"{mean_diff:+.4f} percentage points"
    )

    print(
        f"Median difference: "
        f"{median_diff:+.4f}"
    )

    print(
        f"95% CI: "
        f"[{ci_lower:+.4f}, "
        f"{ci_upper:+.4f}]"
    )

    print(
        f"Cohen's dz: "
        f"{cohens_dz:.3f}"
    )

    print()

    print(
        f"Paired t-test p: "
        f"{t_test.pvalue:.8f}"
    )

    print(
        f"Wilcoxon p: "
        f"{wilcoxon_test.pvalue:.8f}"
    )

    print()

    print(
        f"Greater dropoff in final: "
        f"{greater_percent:.1f}%"
    )

    print(
        f"Lower dropoff in final: "
        f"{lower_percent:.1f}%"
    )

    print()

    print(
        f"Bootstrap mean: "
        f"{bootstrap_means.mean():.4f}"
    )

    print(
        f"Bootstrap SE: "
        f"{bootstrap_se:.4f}"
    )

    print(
        f"Bootstrap 95% CI: "
        f"[{bootstrap_ci_lower:.4f}, "
        f"{bootstrap_ci_upper:.4f}]"
    )

    print(
        f"P(bootstrap mean > 0): "
        f"{bootstrap_positive:.4f}"
    )

    summary = {
        "sex":
            sex_label,

        "n_pairs":
            n,

        "semifinal_mean":
            semi.mean(),

        "final_mean":
            final.mean(),

        "mean_difference":
            mean_diff,

        "median_difference":
            median_diff,

        "sd_difference":
            sd_diff,

        "ci_lower":
            ci_lower,

        "ci_upper":
            ci_upper,

        "cohens_dz":
            cohens_dz,

        "paired_t_p":
            t_test.pvalue,

        "wilcoxon_p":
            wilcoxon_test.pvalue,

        "greater_final_percent":
            greater_percent,

        "lower_final_percent":
            lower_percent
    }

    bootstrap_summary = {
        "sex":
            sex_label,

        "n_pairs":
            n,

        "bootstrap_reps":
            BOOTSTRAP_REPS,

        "observed_mean":
            mean_diff,

        "bootstrap_mean":
            bootstrap_means.mean(),

        "bootstrap_se":
            bootstrap_se,

        "bootstrap_ci_lower":
            bootstrap_ci_lower,

        "bootstrap_ci_upper":
            bootstrap_ci_upper,

        "bootstrap_positive_probability":
            bootstrap_positive
    }

    return (
        paired,
        summary,
        bootstrap_summary
    )


# ============================================================
# RUN ANALYSES
# ============================================================

men_pairs, men_summary, men_bootstrap = (
    analyze_sex(
        MEN_FILE,
        "Men"
    )
)

women_pairs, women_summary, women_bootstrap = (
    analyze_sex(
        WOMEN_FILE,
        "Women"
    )
)


summary_df = pd.DataFrame(
    [
        men_summary,
        women_summary
    ]
)


bootstrap_df = pd.DataFrame(
    [
        men_bootstrap,
        women_bootstrap
    ]
)


summary_df.to_csv(
    TABLE_OUTPUT,
    index=False
)


bootstrap_df.to_csv(
    BOOTSTRAP_OUTPUT,
    index=False
)


# ============================================================
# FIGURE 1
# PAIRED TRAJECTORIES
# ============================================================

for sex_label, paired in [
    (
        "Men",
        men_pairs
    ),
    (
        "Women",
        women_pairs
    )
]:

    fig, ax = plt.subplots(
        figsize=(
            7,
            6
        )
    )

    for _, row in paired.iterrows():

        ax.plot(
            [
                0,
                1
            ],
            [
                row[
                    "semifinal_dropoff"
                ],
                row[
                    "final_dropoff"
                ]
            ],
            alpha=0.25,
            linewidth=1
        )

    means = [
        paired[
            "semifinal_dropoff"
        ].mean(),

        paired[
            "final_dropoff"
        ].mean()
    ]

    ax.plot(
        [
            0,
            1
        ],
        means,
        marker="o",
        linewidth=3,
        markersize=8,
        label="Mean"
    )

    ax.set_xticks(
        [
            0,
            1
        ]
    )

    ax.set_xticklabels(
        [
            "Semifinal",
            "Final"
        ]
    )

    ax.set_ylabel(
        "Dropoff (%)"
    )

    ax.set_title(
        f"{sex_label}: Semifinal to Final Pacing Change"
    )

    ax.legend()

    plt.tight_layout()

    file_name = (
        FIGURE_DIR
        / (
            sex_label.lower()
            + "_paired_semifinal_final.png"
        )
    )

    plt.savefig(
        file_name,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


# ============================================================
# FIGURE 2
# DIFFERENCE DISTRIBUTIONS
# ============================================================

for sex_label, paired in [
    (
        "Men",
        men_pairs
    ),
    (
        "Women",
        women_pairs
    )
]:

    fig, ax = plt.subplots(
        figsize=(
            7,
            5
        )
    )

    ax.hist(
        paired[
            "difference"
        ],
        bins=20
    )

    ax.axvline(
        0,
        linewidth=1
    )

    ax.axvline(
        paired[
            "difference"
        ].mean(),
        linewidth=2,
        linestyle="--"
    )

    ax.set_xlabel(
        "Final minus semifinal dropoff (percentage points)"
    )

    ax.set_ylabel(
        "Number of paired swims"
    )

    ax.set_title(
        f"{sex_label}: Distribution of Pacing Change"
    )

    plt.tight_layout()

    file_name = (
        FIGURE_DIR
        / (
            sex_label.lower()
            + "_difference_distribution.png"
        )
    )

    plt.savefig(
        file_name,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


# ============================================================
# FIGURE 3
# MAIN RESULT FIGURE
# ============================================================

plot_df = pd.DataFrame({
    "Sex": [
        "Men",
        "Men",
        "Women",
        "Women"
    ],

    "Round": [
        "Semifinal",
        "Final",
        "Semifinal",
        "Final"
    ],

    "Mean": [
        men_pairs[
            "semifinal_dropoff"
        ].mean(),

        men_pairs[
            "final_dropoff"
        ].mean(),

        women_pairs[
            "semifinal_dropoff"
        ].mean(),

        women_pairs[
            "final_dropoff"
        ].mean()
    ],

    "SE": [
        men_pairs[
            "semifinal_dropoff"
        ].std(
            ddof=1
        )
        /
        np.sqrt(
            len(
                men_pairs
            )
        ),

        men_pairs[
            "final_dropoff"
        ].std(
            ddof=1
        )
        /
        np.sqrt(
            len(
                men_pairs
            )
        ),

        women_pairs[
            "semifinal_dropoff"
        ].std(
            ddof=1
        )
        /
        np.sqrt(
            len(
                women_pairs
            )
        ),

        women_pairs[
            "final_dropoff"
        ].std(
            ddof=1
        )
        /
        np.sqrt(
            len(
                women_pairs
            )
        )
    ]
})


plot_df[
    "CI"
] = (
    1.96
    *
    plot_df[
        "SE"
    ]
)


x_positions = [
    0,
    1,
    3,
    4
]


fig, ax = plt.subplots(
    figsize=(
        9,
        6
    )
)


ax.bar(
    x_positions,
    plot_df[
        "Mean"
    ],
    yerr=plot_df[
        "CI"
    ],
    capsize=5
)


ax.set_xticks(
    x_positions
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
    "Mean dropoff (%)"
)


ax.set_title(
    "Second-Half Pacing Deterioration Increases in Finals"
)


for x, mean in zip(
    x_positions,
    plot_df[
        "Mean"
    ]
):

    ax.text(
        x,
        mean + 0.25,
        f"{mean:.2f}%",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold"
    )


plt.tight_layout()


main_figure = (
    FIGURE_DIR
    / "main_semifinal_final_result.png"
)


plt.savefig(
    main_figure,
    dpi=300,
    bbox_inches="tight"
)


plt.close()


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 80)
print("SEMIFINAL-FINAL ANALYSIS COMPLETE")
print("=" * 80)

print()

print(
    f"Summary table saved to:"
)

print(
    TABLE_OUTPUT
)

print()

print(
    f"Bootstrap table saved to:"
)

print(
    BOOTSTRAP_OUTPUT
)

print()

print(
    "Figures saved to:"
)

print(
    FIGURE_DIR
)
