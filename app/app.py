import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_FILE = (
    PROJECT_ROOT
    / "data"
    / "swimming_analysis.db"
)

MECHANISM_FIGURE = (
    PROJECT_ROOT
    / "outputs"
    / "figures"
    / "semifinal_final_mechanism.png"
)


# ============================================================
# PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="Elite 100m Freestyle Analysis",
    page_icon="🏊",
    layout="wide"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    connection = sqlite3.connect(DATABASE_FILE)

    elite = pd.read_sql_query(
        """
        SELECT *
        FROM elite_race_results
        """,
        connection
    )

    athletes = pd.read_sql_query(
        """
        SELECT *
        FROM athletes
        """,
        connection
    )

    connection.close()

    return elite, athletes


elite, athletes = load_data()


# ============================================================
# TITLE
# ============================================================

st.title(
    "Elite 100m Freestyle Performance Analysis"
)

st.write(
    """
    Interactive analysis of elite men's and women's 100m freestyle
    performances from Olympic Games and World Championships between
    2000 and 2025.
    """
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header(
    "Filters"
)

sex_filter = st.sidebar.selectbox(
    "Sex",
    [
        "All",
        "Men",
        "Women"
    ]
)

round_filter = st.sidebar.selectbox(
    "Race Round",
    [
        "All",
        "Semifinals",
        "Finals"
    ]
)

year_min = int(
    elite["competition_year"].min()
)

year_max = int(
    elite["competition_year"].max()
)

year_range = st.sidebar.slider(
    "Competition Year",
    min_value=year_min,
    max_value=year_max,
    value=(
        year_min,
        year_max
    )
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = elite.copy()

if sex_filter != "All":

    filtered = filtered[
        filtered["sex"] == sex_filter
    ]

if round_filter != "All":

    filtered = filtered[
        filtered["race_round"] == round_filter
    ]

filtered = filtered[
    filtered["competition_year"].between(
        year_range[0],
        year_range[1]
    )
]


# A second dataset used for analyses that require both rounds.
# This respects sex and year filters but ignores the round filter.

analysis_filtered = elite[
    elite["competition_year"].between(
        year_range[0],
        year_range[1]
    )
].copy()

if sex_filter != "All":

    analysis_filtered = analysis_filtered[
        analysis_filtered["sex"] == sex_filter
    ]


# ============================================================
# KEY FINDINGS
# ============================================================

st.subheader(
    "Key Findings"
)

st.markdown(
    """
    - **Finals are faster overall** than semifinals for both men and women.
    - **Swimmers tend to open faster in finals**, especially during the first 50 m.
    - **The Second-Half Difference tends to increase in finals**, indicating greater slowing during the second half of the race.
    """
)


# ============================================================
# SELECTED SAMPLE
# ============================================================

st.subheader(
    "Selected Sample"
)

if sex_filter == "All":

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Race Observations",
        f"{len(filtered):,}"
    )

    col2.metric(
        "Unique Swimmers",
        f"{filtered['swimmer_id'].nunique():,}"
    )

    men_filtered = filtered[
        filtered["sex"] == "Men"
    ]

    women_filtered = filtered[
        filtered["sex"] == "Women"
    ]

    if len(men_filtered) > 0:

        col3.metric(
            "Men - Average Final Time",
            f"{men_filtered['final_time'].mean():.2f} s"
        )

    else:

        col3.metric(
            "Men - Average Final Time",
            "N/A"
        )

    if len(women_filtered) > 0:

        col4.metric(
            "Women - Average Final Time",
            f"{women_filtered['final_time'].mean():.2f} s"
        )

    else:

        col4.metric(
            "Women - Average Final Time",
            "N/A"
        )

else:

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Race Observations",
        f"{len(filtered):,}"
    )

    col2.metric(
        "Unique Swimmers",
        f"{filtered['swimmer_id'].nunique():,}"
    )

    if len(filtered) > 0:

        col3.metric(
            "Average Final Time",
            f"{filtered['final_time'].mean():.2f} s"
        )

        col4.metric(
            "Average Second-Half Difference",
            f"{filtered['dropoff_seconds'].mean():.2f} s"
        )

    else:

        col3.metric(
            "Average Final Time",
            "N/A"
        )

        col4.metric(
            "Average Second-Half Difference",
            "N/A"
        )


# ============================================================
# SECOND-HALF DIFFERENCE EXPLANATION
# ============================================================

st.info(
    """
    **What is Second-Half Difference?**

    Second-Half Difference measures how many seconds longer the swimmer
    took to complete the second 50 m compared with the first 50 m.

    **Second-Half Difference = Second 50 m - First 50 m**

    For example, if a swimmer completes the first 50 m in 23.00 seconds
    and the second 50 m in 25.10 seconds, the Second-Half Difference is
    2.10 seconds.

    A larger value indicates greater slowing during the second half
    of the race.
    """
)

st.divider()


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Overview",
        "Semifinal vs Final",
        "Athlete Explorer",
        "Physical Characteristics"
    ]
)


# ============================================================
# TAB 1 - OVERVIEW
# ============================================================

with tab1:

    st.header(
        "Performance Overview"
    )

    # ========================================================
    # PERFORMANCE TABLE
    # ========================================================

    st.subheader(
        "Performance and Pacing by Race Round"
    )

    pacing_summary = (
        filtered
        .groupby(
            [
                "sex",
                "race_round"
            ],
            as_index=False
        )
        .agg(
            average_first_50=(
                "first_50",
                "mean"
            ),
            average_second_50=(
                "second_50",
                "mean"
            ),
            average_second_half_difference=(
                "dropoff_seconds",
                "mean"
            ),
            average_final_time=(
                "final_time",
                "mean"
            ),
            races=(
                "final_time",
                "size"
            )
        )
    )

    pacing_summary = pacing_summary.rename(
        columns={
            "sex": "Sex",
            "race_round": "Race Round",
            "average_first_50":
                "Average First 50 (s)",
            "average_second_50":
                "Average Second 50 (s)",
            "average_second_half_difference":
                "Second-Half Difference (s)",
            "average_final_time":
                "Average Final Time (s)",
            "races":
                "Races"
        }
    )

    numeric_columns = [
        "Average First 50 (s)",
        "Average Second 50 (s)",
        "Second-Half Difference (s)",
        "Average Final Time (s)"
    ]

    if not pacing_summary.empty:

        pacing_summary[
            numeric_columns
        ] = pacing_summary[
            numeric_columns
        ].round(2)

    st.dataframe(
        pacing_summary[
            [
                "Sex",
                "Race Round",
                "Average First 50 (s)",
                "Average Second 50 (s)",
                "Second-Half Difference (s)",
                "Average Final Time (s)",
                "Races"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # FINAL TIME BY ROUND
    # ========================================================

    st.subheader(
        "Average Final Time by Race Round"
    )

    st.write(
        """
        Men's and women's performances are shown separately.
        Within each chart, semifinal and final performances can
        be compared directly.
        """
    )

    round_order = [
        "Semifinals",
        "Finals"
    ]

    # ========================================================
    # MEN SUMMARY
    # ========================================================

    men_final_summary = (
        filtered[
            filtered["sex"] == "Men"
        ]
        .groupby(
            "race_round",
            as_index=False
        )
        .agg(
            average_final_time=(
                "final_time",
                "mean"
            )
        )
    )

    if not men_final_summary.empty:

        men_final_summary[
            "race_round"
        ] = pd.Categorical(
            men_final_summary[
                "race_round"
            ],
            categories=round_order,
            ordered=True
        )

        men_final_summary = (
            men_final_summary
            .sort_values(
                "race_round"
            )
        )

    # ========================================================
    # WOMEN SUMMARY
    # ========================================================

    women_final_summary = (
        filtered[
            filtered["sex"] == "Women"
        ]
        .groupby(
            "race_round",
            as_index=False
        )
        .agg(
            average_final_time=(
                "final_time",
                "mean"
            )
        )
    )

    if not women_final_summary.empty:

        women_final_summary[
            "race_round"
        ] = pd.Categorical(
            women_final_summary[
                "race_round"
            ],
            categories=round_order,
            ordered=True
        )

        women_final_summary = (
            women_final_summary
            .sort_values(
                "race_round"
            )
        )

    men_col, women_col = st.columns(2)

    # ========================================================
    # MEN FINAL TIME FIGURE
    # ========================================================

    with men_col:

        st.markdown(
            "### Men"
        )

        if not men_final_summary.empty:

            fig_men, ax_men = plt.subplots(
                figsize=(6, 4.5)
            )

            ax_men.bar(
                men_final_summary[
                    "race_round"
                ].astype(str),
                men_final_summary[
                    "average_final_time"
                ]
            )

            ax_men.set_title(
                "Men - Average Final Time"
            )

            ax_men.set_xlabel(
                "Race Round"
            )

            ax_men.set_ylabel(
                "Final Time (seconds)"
            )

            ax_men.tick_params(
                axis="x",
                rotation=0
            )

            minimum_men = (
                men_final_summary[
                    "average_final_time"
                ].min()
            )

            maximum_men = (
                men_final_summary[
                    "average_final_time"
                ].max()
            )

            ax_men.set_ylim(
                minimum_men - 1,
                maximum_men + 1
            )

            for i, value in enumerate(
                men_final_summary[
                    "average_final_time"
                ]
            ):

                ax_men.text(
                    i,
                    value + 0.05,
                    f"{value:.2f} s",
                    ha="center",
                    va="bottom",
                    fontweight="bold"
                )

            plt.tight_layout()

            st.pyplot(
                fig_men,
                use_container_width=True
            )

            plt.close(
                fig_men
            )

        else:

            st.info(
                "No men's observations for the selected filters."
            )

    # ========================================================
    # WOMEN FINAL TIME FIGURE
    # ========================================================

    with women_col:

        st.markdown(
            "### Women"
        )

        if not women_final_summary.empty:

            fig_women, ax_women = plt.subplots(
                figsize=(6, 4.5)
            )

            ax_women.bar(
                women_final_summary[
                    "race_round"
                ].astype(str),
                women_final_summary[
                    "average_final_time"
                ]
            )

            ax_women.set_title(
                "Women - Average Final Time"
            )

            ax_women.set_xlabel(
                "Race Round"
            )

            ax_women.set_ylabel(
                "Final Time (seconds)"
            )

            ax_women.tick_params(
                axis="x",
                rotation=0
            )

            minimum_women = (
                women_final_summary[
                    "average_final_time"
                ].min()
            )

            maximum_women = (
                women_final_summary[
                    "average_final_time"
                ].max()
            )

            ax_women.set_ylim(
                minimum_women - 1,
                maximum_women + 1
            )

            for i, value in enumerate(
                women_final_summary[
                    "average_final_time"
                ]
            ):

                ax_women.text(
                    i,
                    value + 0.05,
                    f"{value:.2f} s",
                    ha="center",
                    va="bottom",
                    fontweight="bold"
                )

            plt.tight_layout()

            st.pyplot(
                fig_women,
                use_container_width=True
            )

            plt.close(
                fig_women
            )

        else:

            st.info(
                "No women's observations for the selected filters."
            )

    # ========================================================
    # PERFORMANCE TREND OVER TIME
    # ========================================================

    st.subheader(
        "Performance Trend Over Time"
    )

    st.write(
        """
        Average elite 100 m freestyle performance by competition year.
        Men and women are displayed separately.
        """
    )

    yearly_performance = (
        filtered
        .groupby(
            [
                "competition_year",
                "sex"
            ],
            as_index=False
        )
        .agg(
            average_final_time=(
                "final_time",
                "mean"
            )
        )
    )

    trend_col1, trend_col2 = st.columns(2)

    # ========================================================
    # MEN TREND
    # ========================================================

    with trend_col1:

        st.markdown(
            "### Men"
        )

        men_yearly = yearly_performance[
            yearly_performance[
                "sex"
            ] == "Men"
        ]

        if not men_yearly.empty:

            fig, ax = plt.subplots(
                figsize=(7, 4)
            )

            ax.plot(
                men_yearly[
                    "competition_year"
                ],
                men_yearly[
                    "average_final_time"
                ],
                marker="o"
            )

            ax.set_xlabel(
                "Year"
            )

            ax.set_ylabel(
                "Average Final Time (seconds)"
            )

            ax.set_title(
                "Men - Performance Over Time"
            )

            ax.tick_params(
                axis="x",
                rotation=45
            )

            plt.tight_layout()

            st.pyplot(
                fig,
                use_container_width=True
            )

            plt.close(fig)

        else:

            st.info(
                "No men's data for the selected filters."
            )

    # ========================================================
    # WOMEN TREND
    # ========================================================

    with trend_col2:

        st.markdown(
            "### Women"
        )

        women_yearly = yearly_performance[
            yearly_performance[
                "sex"
            ] == "Women"
        ]

        if not women_yearly.empty:

            fig, ax = plt.subplots(
                figsize=(7, 4)
            )

            ax.plot(
                women_yearly[
                    "competition_year"
                ],
                women_yearly[
                    "average_final_time"
                ],
                marker="o"
            )

            ax.set_xlabel(
                "Year"
            )

            ax.set_ylabel(
                "Average Final Time (seconds)"
            )

            ax.set_title(
                "Women - Performance Over Time"
            )

            ax.tick_params(
                axis="x",
                rotation=45
            )

            plt.tight_layout()

            st.pyplot(
                fig,
                use_container_width=True
            )

            plt.close(fig)

        else:

            st.info(
                "No women's data for the selected filters."
            )

    # ========================================================
    # FASTEST PERFORMANCES
    # ========================================================

    st.subheader(
        "Fastest Elite Performances"
    )

    fastest = (
        filtered[
            [
                "swimmer_name",
                "final_time",
                "sex",
                "competition_year",
                "race_round",
                "first_50",
                "second_50",
                "dropoff_seconds",
                "meet_name"
            ]
        ]
        .sort_values(
            "final_time"
        )
        .head(20)
        .copy()
    )

    fastest = fastest.rename(
        columns={
            "swimmer_name":
                "Swimmer",
            "final_time":
                "Final Time (s)",
            "sex":
                "Sex",
            "competition_year":
                "Year",
            "race_round":
                "Race Round",
            "first_50":
                "First 50 (s)",
            "second_50":
                "Second 50 (s)",
            "dropoff_seconds":
                "Second-Half Difference (s)",
            "meet_name":
                "Competition"
        }
    )

    numeric_columns = [
        "Final Time (s)",
        "First 50 (s)",
        "Second 50 (s)",
        "Second-Half Difference (s)"
    ]

    if not fastest.empty:

        fastest[
            numeric_columns
        ] = fastest[
            numeric_columns
        ].round(2)

    # Bold final-time values
    styled_fastest = fastest.style.map(
        lambda value: (
            "font-weight: bold; "
            "font-size: 16px;"
        ),
        subset=[
            "Final Time (s)"
        ]
    )

    st.dataframe(
        styled_fastest,
        column_order=[
            "Swimmer",
            "Final Time (s)",
            "Sex",
            "Year",
            "Race Round",
            "First 50 (s)",
            "Second 50 (s)",
            "Second-Half Difference (s)",
            "Competition"
        ],
        column_config={
            "Swimmer":
                st.column_config.TextColumn(
                    "Swimmer",
                    width="medium"
                ),
            "Final Time (s)":
                st.column_config.NumberColumn(
                    "Final Time (s)",
                    format="%.2f s",
                    width="small"
                ),
            "Sex":
                st.column_config.TextColumn(
                    "Sex",
                    width="small"
                ),
            "Year":
                st.column_config.NumberColumn(
                    "Year",
                    format="%d",
                    width="small"
                ),
            "Race Round":
                st.column_config.TextColumn(
                    "Race Round",
                    width="small"
                ),
            "First 50 (s)":
                st.column_config.NumberColumn(
                    "First 50 (s)",
                    format="%.2f",
                    width="small"
                ),
            "Second 50 (s)":
                st.column_config.NumberColumn(
                    "Second 50 (s)",
                    format="%.2f",
                    width="small"
                ),
            "Second-Half Difference (s)":
                st.column_config.NumberColumn(
                    "Second-Half Difference (s)",
                    format="%.2f",
                    width="small"
                ),
            "Competition":
                st.column_config.TextColumn(
                    "Competition",
                    width="large"
                )
        },
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 2 - SEMIFINAL VS FINAL
# ============================================================

with tab2:

    st.header(
        "Semifinal vs Final"
    )

    st.write(
        """
        This analysis compares swimmers who competed in both the
        semifinal and final of the same competition.
        """
    )

    # ========================================================
    # PAIRED DATASET
    # ========================================================

    paired_source = analysis_filtered[
        analysis_filtered[
            "race_round"
        ].isin(
            [
                "Semifinals",
                "Finals"
            ]
        )
    ].copy()

    paired = (
        paired_source
        .pivot_table(
            index=[
                "competition_id",
                "swimmer_id",
                "swimmer_name",
                "sex"
            ],
            columns="race_round",
            values="dropoff_seconds",
            aggfunc="mean"
        )
        .reset_index()
    )

    paired = paired.dropna(
        subset=[
            "Semifinals",
            "Finals"
        ]
    )

    men_paired = paired[
        paired["sex"] == "Men"
    ].copy()

    women_paired = paired[
        paired["sex"] == "Women"
    ].copy()

    # ========================================================
    # SUMMARY METRICS
    # ========================================================

    metrics_col1, metrics_col2 = st.columns(2)

    with metrics_col1:

        st.subheader(
            "Men"
        )

        if not men_paired.empty:

            men_semi = (
                men_paired[
                    "Semifinals"
                ].mean()
            )

            men_final = (
                men_paired[
                    "Finals"
                ].mean()
            )

            st.metric(
                "Semifinal Second-Half Difference",
                f"{men_semi:.2f} s"
            )

            st.metric(
                "Final Second-Half Difference",
                f"{men_final:.2f} s"
            )

            st.metric(
                "Change",
                f"{men_final - men_semi:+.2f} s"
            )

        else:

            st.info(
                "No paired men's observations for the selected years."
            )

    with metrics_col2:

        st.subheader(
            "Women"
        )

        if not women_paired.empty:

            women_semi = (
                women_paired[
                    "Semifinals"
                ].mean()
            )

            women_final = (
                women_paired[
                    "Finals"
                ].mean()
            )

            st.metric(
                "Semifinal Second-Half Difference",
                f"{women_semi:.2f} s"
            )

            st.metric(
                "Final Second-Half Difference",
                f"{women_final:.2f} s"
            )

            st.metric(
                "Change",
                f"{women_final - women_semi:+.2f} s"
            )

        else:

            st.info(
                "No paired women's observations for the selected years."
            )

    # ========================================================
    # PAIRED SEMIFINAL-FINAL COMPARISON
    # ========================================================

    st.subheader(
        "Paired Semifinal-to-Final Comparison"
    )

    st.write(
        """
        Each thin line represents the same swimmer within the same
        competition. This allows semifinal and final pacing to be
        compared within the same athlete.
        """
    )

    paired_col1, paired_col2 = st.columns(2)

    # ========================================================
    # MEN PAIRED FIGURE
    # ========================================================

    with paired_col1:

        st.markdown(
            "### Men"
        )

        if not men_paired.empty:

            fig, ax = plt.subplots(
                figsize=(6, 5)
            )

            for _, row in men_paired.iterrows():

                ax.plot(
                    [
                        "Semifinal",
                        "Final"
                    ],
                    [
                        row["Semifinals"],
                        row["Finals"]
                    ],
                    marker="o",
                    alpha=0.20
                )

            ax.plot(
                [
                    "Semifinal",
                    "Final"
                ],
                [
                    men_paired[
                        "Semifinals"
                    ].mean(),
                    men_paired[
                        "Finals"
                    ].mean()
                ],
                marker="o",
                linewidth=3,
                label="Mean"
            )

            ax.set_ylabel(
                "Second-Half Difference (seconds)"
            )

            ax.set_title(
                "Men"
            )

            ax.legend()

            plt.tight_layout()

            st.pyplot(
                fig,
                use_container_width=True
            )

            plt.close(fig)

        else:

            st.info(
                "No paired men's observations."
            )

    # ========================================================
    # WOMEN PAIRED FIGURE
    # ========================================================

    with paired_col2:

        st.markdown(
            "### Women"
        )

        if not women_paired.empty:

            fig, ax = plt.subplots(
                figsize=(6, 5)
            )

            for _, row in women_paired.iterrows():

                ax.plot(
                    [
                        "Semifinal",
                        "Final"
                    ],
                    [
                        row["Semifinals"],
                        row["Finals"]
                    ],
                    marker="o",
                    alpha=0.20
                )

            ax.plot(
                [
                    "Semifinal",
                    "Final"
                ],
                [
                    women_paired[
                        "Semifinals"
                    ].mean(),
                    women_paired[
                        "Finals"
                    ].mean()
                ],
                marker="o",
                linewidth=3,
                label="Mean"
            )

            ax.set_ylabel(
                "Second-Half Difference (seconds)"
            )

            ax.set_title(
                "Women"
            )

            ax.legend()

            plt.tight_layout()

            st.pyplot(
                fig,
                use_container_width=True
            )

            plt.close(fig)

        else:

            st.info(
                "No paired women's observations."
            )

    # ========================================================
    # MECHANISM FIGURE
    # ========================================================

    st.subheader(
        "How Performance Changes from Semifinal to Final"
    )

    if MECHANISM_FIGURE.exists():

        left_space, center_image, right_space = st.columns(
            [
                1.5,
                3,
                1.5
            ]
        )

        with center_image:

            st.image(
                str(
                    MECHANISM_FIGURE
                ),
                caption=(
                    "Change from semifinal to final. "
                    "Negative time values indicate faster swimming."
                ),
                use_container_width=True
            )

    else:

        st.warning(
            "Mechanism figure was not found."
        )

    st.write(
        """
        Swimmers generally record faster overall times in finals,
        driven primarily by a faster opening 50 m.

        At the same time, the difference between the first and second
        50 m becomes larger. This means that swimmers tend to slow
        more during the second half of the final than during the
        semifinal.

        These results describe statistical associations and should
        not be interpreted as causal effects.
        """
    )


# ============================================================
# TAB 3 - ATHLETE EXPLORER
# ============================================================

with tab3:

    st.header(
        "Athlete Explorer"
    )

    swimmers = sorted(
        analysis_filtered[
            "swimmer_name"
        ]
        .dropna()
        .unique()
    )

    if len(swimmers) > 0:

        selected_swimmer = st.selectbox(
            "Select a swimmer",
            swimmers
        )

        swimmer_data = (
            analysis_filtered[
                analysis_filtered[
                    "swimmer_name"
                ] == selected_swimmer
            ]
            .sort_values(
                [
                    "competition_year",
                    "race_round"
                ]
            )
            .copy()
        )

        # ====================================================
        # ATHLETE SUMMARY
        # ====================================================

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Elite Races",
            len(
                swimmer_data
            )
        )

        c2.metric(
            "Best Final Time",
            f"{swimmer_data['final_time'].min():.2f} s"
        )

        c3.metric(
            "Average Final Time",
            f"{swimmer_data['final_time'].mean():.2f} s"
        )

        c4.metric(
            "Average Second-Half Difference",
            f"{swimmer_data['dropoff_seconds'].mean():.2f} s"
        )

        # ====================================================
        # ATHLETE TABLE
        # ====================================================

        st.subheader(
            "Race History"
        )

        athlete_table = swimmer_data[
            [
                "competition_year",
                "meet_name",
                "race_round",
                "first_50",
                "second_50",
                "dropoff_seconds",
                "final_time"
            ]
        ].copy()

        athlete_table = athlete_table.rename(
            columns={
                "competition_year":
                    "Year",
                "meet_name":
                    "Competition",
                "race_round":
                    "Race Round",
                "first_50":
                    "First 50 (s)",
                "second_50":
                    "Second 50 (s)",
                "dropoff_seconds":
                    "Second-Half Difference (s)",
                "final_time":
                    "Final Time (s)"
            }
        )

        numeric_columns = [
            "First 50 (s)",
            "Second 50 (s)",
            "Second-Half Difference (s)",
            "Final Time (s)"
        ]

        athlete_table[
            numeric_columns
        ] = athlete_table[
            numeric_columns
        ].round(2)

        st.dataframe(
            athlete_table[
                [
                    "Year",
                    "Final Time (s)",
                    "Race Round",
                    "First 50 (s)",
                    "Second 50 (s)",
                    "Second-Half Difference (s)",
                    "Competition"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        # ====================================================
        # ATHLETE CHARTS
        # ====================================================

        chart1, chart2 = st.columns(2)

        with chart1:

            st.markdown(
                "### Final Time Across Competitions"
            )

            time_trend = (
                swimmer_data
                .pivot_table(
                    index="competition_year",
                    columns="race_round",
                    values="final_time",
                    aggfunc="mean"
                )
                .sort_index()
            )

            st.line_chart(
                time_trend,
                height=320
            )

        with chart2:

            st.markdown(
                "### Second-Half Difference Across Competitions"
            )

            difference_trend = (
                swimmer_data
                .pivot_table(
                    index="competition_year",
                    columns="race_round",
                    values="dropoff_seconds",
                    aggfunc="mean"
                )
                .sort_index()
            )

            st.line_chart(
                difference_trend,
                height=320
            )

    else:

        st.info(
            "No athletes are available for the selected filters."
        )


# ============================================================
# TAB 4 - PHYSICAL CHARACTERISTICS
# ============================================================

with tab4:

    st.header(
        "Physical Characteristics"
    )

    height_available = (
        athletes[
            "height_cm"
        ]
        .notna()
        .sum()
    )

    weight_available = (
        athletes[
            "weight_kg"
        ]
        .notna()
        .sum()
    )

    # ========================================================
    # PHYSICAL SUMMARY
    # ========================================================

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Athletes",
        len(
            athletes
        )
    )

    c2.metric(
        "Height Available",
        f"{height_available} / {len(athletes)}"
    )

    c3.metric(
        "Weight Available",
        f"{weight_available} / {len(athletes)}"
    )

    # ========================================================
    # HEIGHT COVERAGE
    # ========================================================

    st.subheader(
        "Height Data Coverage"
    )

    height_coverage = (
        athletes
        .groupby(
            "sex"
        )
        .agg(
            athletes=(
                "swimmer_id",
                "count"
            ),
            height_available=(
                "height_cm",
                "count"
            )
        )
        .reset_index()
    )

    height_coverage[
        "coverage_percent"
    ] = (
        height_coverage[
            "height_available"
        ]
        /
        height_coverage[
            "athletes"
        ]
        * 100
    ).round(1)

    height_coverage = (
        height_coverage.rename(
            columns={
                "sex":
                    "Sex",
                "athletes":
                    "Athletes",
                "height_available":
                    "Height Available",
                "coverage_percent":
                    "Coverage (%)"
            }
        )
    )

    st.dataframe(
        height_coverage,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # MERGE PHYSICAL DATA
    # ========================================================

    physical_races = elite.merge(
        athletes[
            [
                "swimmer_id",
                "height_cm",
                "weight_kg"
            ]
        ],
        on="swimmer_id",
        how="left"
    )

    physical_races = physical_races[
        physical_races[
            "height_cm"
        ].notna()
    ]

    # ========================================================
    # HEIGHT AND FINAL TIME
    # ========================================================

    st.subheader(
        "Height and Final Time"
    )

    physical_sex = st.selectbox(
        "Select sex for height analysis",
        [
            "Men",
            "Women"
        ]
    )

    physical_filtered = (
        physical_races[
            physical_races[
                "sex"
            ] == physical_sex
        ][
            [
                "height_cm",
                "final_time"
            ]
        ]
        .dropna()
        .rename(
            columns={
                "height_cm":
                    "Height (cm)",
                "final_time":
                    "Final Time (s)"
            }
        )
    )

    st.scatter_chart(
        physical_filtered,
        x="Height (cm)",
        y="Final Time (s)",
        height=400
    )

    # ========================================================
    # PHYSICAL INTERPRETATION
    # ========================================================

    st.subheader(
        "Statistical Interpretation"
    )

    st.write(
        """
        In repeated-measures GEE models, height was not clearly
        associated with men's 100 m freestyle performance.

        Among women, greater height was associated with faster
        final times and particularly faster second-half performance.

        Formal height-by-sex interaction tests were significant
        for final time and second 50 m performance.

        Physical-data results should be interpreted cautiously
        because historical height and weight coverage is incomplete.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    """
    Data source: World Aquatics API | Physical data: Wikidata |
    Analysis: Python, SQLite, SQL, statsmodels
    """
)
