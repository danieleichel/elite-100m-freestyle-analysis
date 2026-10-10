import pandas as pd
import streamlit as st


def render_statistical_analysis():

    # ========================================================
    # TITLE
    # ========================================================

    st.header(
        "Statistical Analysis"
    )

    st.write(
        """
        This section presents the inferential statistical analyses
        behind the project.

        These results are based on the full pre-specified analysis
        sample rather than the interactive sidebar filters.
        """
    )

    st.info(
        """
        **Why are percentages used here when the dashboard uses seconds?**

        The dashboard presents **Second-Half Difference (seconds)**
        because it is easier to interpret directly.

        The main statistical pacing analyses use **percentage dropoff**,
        calculated relative to the first 50 m. This provides a normalized
        pacing measure and is especially useful when comparing athletes
        with different absolute swimming speeds.
        """
    )

    # ========================================================
    # 1. PRIMARY PAIRED ANALYSIS
    # ========================================================

    st.subheader(
        "1. Primary Paired Semifinal-to-Final Analysis"
    )

    st.write(
        """
        The primary analysis compares the same swimmer in the semifinal
        and final of the same competition.

        This paired design reduces between-swimmer variability because
        each athlete is compared with themselves.
        """
    )

    paired_results = pd.DataFrame(
        {
            "Sex": [
                "Men",
                "Women"
            ],
            "Paired Swimmers": [
                136,
                144
            ],
            "Mean Change in Pacing (percentage points)": [
                0.82,
                0.91
            ],
            "Bootstrap 95% CI": [
                "0.48 to 1.16",
                "0.63 to 1.19"
            ],
            "Cohen's dz": [
                0.40,
                0.53
            ],
            "Paired t-test": [
                "p < 0.001",
                "p < 0.001"
            ],
            "Wilcoxon Test": [
                "p < 0.001",
                "p < 0.001"
            ]
        }
    )

    st.dataframe(
        paired_results,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        """
        **Interpretation**

        Both men and women showed a statistically significant increase
        in second-half pacing deterioration from semifinal to final.

        The estimated standardized effect was moderate, with a somewhat
        larger effect among women.
        """
    )

    # ========================================================
    # 2. SEMIFINAL-TO-FINAL MECHANISM
    # ========================================================

    st.subheader(
        "2. What Changed from Semifinal to Final?"
    )

    st.write(
        """
        These values show average within-swimmer changes from semifinal
        to final in seconds.

        A negative value indicates that the swimmer was faster in the
        final. A positive value indicates that the swimmer was slower.
        """
    )

    mechanism_results = pd.DataFrame(
        {
            "Measure": [
                "First 50 m",
                "Second 50 m",
                "Final 100 m Time",
                "Second-Half Difference"
            ],
            "Men Change (s)": [
                -0.133,
                0.043,
                -0.090,
                0.176
            ],
            "Women Change (s)": [
                -0.164,
                0.059,
                -0.105,
                0.223
            ]
        }
    )

    st.dataframe(
        mechanism_results,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        """
        **Interpretation**

        Swimmers were faster overall in finals, but the improvement was
        driven primarily by a faster opening 50 m.

        The second 50 m became slightly slower, producing a larger
        difference between the first and second halves of the race.
        """
    )

    # ========================================================
    # 3. REPEATED-MEASURES MODELING
    # ========================================================

    st.subheader(
        "3. Repeated-Measures Modeling"
    )

    st.write(
        """
        Many swimmers appear multiple times in the dataset across
        competitions and race rounds.

        Performances from the same swimmer are therefore correlated.
        Treating every race as completely independent could produce
        misleading standard errors and statistical conclusions.
        """
    )

    st.markdown(
        """
        The project uses several approaches to address repeated
        observations:

        - **Ordinary Least Squares (OLS)** as a baseline model
        - **Cluster-robust standard errors** clustered by swimmer
        - **Mixed-effects models** with swimmer-level random effects
        - **Generalized Estimating Equations (GEE)** as the primary population-average repeated-measures model
        """
    )

    # ========================================================
    # 4. LONG-TERM PACING TREND
    # ========================================================

    st.subheader(
        "4. Long-Term Pacing Trend"
    )

    st.write(
        """
        These models test whether pacing strategy changed systematically
        over competition years while accounting for repeated observations
        from the same swimmer.
        """
    )

    trend_results = pd.DataFrame(
        {
            "Sex": [
                "Men",
                "Women"
            ],
            "GEE Year Coefficient": [
                -0.0301,
                0.0356
            ],
            "95% CI": [
                "-0.0888 to 0.0286",
                "-0.0066 to 0.0779"
            ],
            "p-value": [
                0.3150,
                0.0985
            ],
            "Conclusion": [
                "No significant trend",
                "No significant trend"
            ]
        }
    )

    st.dataframe(
        trend_results,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        """
        **Interpretation**

        After accounting for repeated observations from the same
        swimmer, there was no statistically convincing evidence of a
        long-term pacing trend for either men or women.

        This is important because a simpler OLS model suggested a decline
        in male pacing dropoff over time. That association weakened after
        swimmer-level dependence was modeled appropriately.
        """
    )

    # ========================================================
    # 5. HEIGHT AND PERFORMANCE
    # ========================================================

    st.subheader(
        "5. Height and Performance"
    )

    st.write(
        """
        Height-performance relationships were estimated using GEE
        models controlling for competition year, age, reaction time,
        race round, and repeated observations from the same swimmer.
        """
    )

    height_results = pd.DataFrame(
        {
            "Sex": [
                "Men",
                "Women"
            ],
            "Height Effect on Final Time (s per cm)": [
                -0.0025,
                -0.0365
            ],
            "p-value": [
                0.8082,
                0.0005
            ],
            "Conclusion": [
                "No clear association",
                "Statistically significant association"
            ]
        }
    )

    st.dataframe(
        height_results,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        """
        **Interpretation**

        Among men, height was not clearly associated with final
        performance.

        Among women, each additional centimeter of height was associated
        with approximately **0.037 seconds faster final time**, after
        adjustment for the other variables in the model.

        This is an observational association and should not be interpreted
        as a causal effect of height.
        """
    )

    # ========================================================
    # 6. HEIGHT-BY-SEX INTERACTION
    # ========================================================

    st.subheader(
        "6. Height-by-Sex Interaction"
    )

    st.write(
        """
        Interaction models formally test whether the association between
        height and swimming performance differs between men and women.
        """
    )

    interaction_results = pd.DataFrame(
        {
            "Outcome": [
                "Final Time",
                "First 50 m",
                "Second 50 m",
                "Pacing Dropoff"
            ],
            "Interaction p-value": [
                0.0337,
                0.4793,
                0.0266,
                0.2922
            ],
            "Evidence of Sex Difference": [
                "Yes",
                "No",
                "Yes",
                "No"
            ]
        }
    )

    st.dataframe(
        interaction_results,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        """
        **Interpretation**

        The height-performance relationship differed significantly
        between men and women for:

        - **Final 100 m time**
        - **Second 50 m performance**

        No statistically significant interaction was detected for:

        - First 50 m performance
        - Pacing dropoff
        """
    )

    # ========================================================
    # 7. STATISTICAL METHODS
    # ========================================================

    st.subheader(
        "7. Statistical Methods Used"
    )

    methods_table = pd.DataFrame(
        {
            "Method": [
                "Descriptive Statistics",
                "Pearson Correlation",
                "Paired t-test",
                "Wilcoxon Signed-Rank Test",
                "Bootstrap Confidence Intervals",
                "Cohen's dz",
                "OLS Regression",
                "Cluster-Robust Regression",
                "Mixed-Effects Models",
                "Generalized Estimating Equations",
                "Interaction Models",
                "Missing-Data Diagnostics"
            ],
            "Purpose": [
                "Summarize race performance and pacing",
                "Measure linear associations",
                "Test mean within-swimmer changes",
                "Provide a nonparametric paired robustness test",
                "Quantify uncertainty around paired estimates",
                "Measure standardized paired effect size",
                "Provide baseline regression estimates",
                "Adjust uncertainty for repeated swimmers",
                "Model swimmer-level random effects",
                "Estimate population-average repeated-measures effects",
                "Test whether associations differ by sex",
                "Evaluate potential bias from incomplete physical data"
            ]
        }
    )

    st.dataframe(
        methods_table,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # 8. STATISTICAL LIMITATIONS
    # ========================================================

    st.subheader(
        "8. Statistical Limitations"
    )

    st.markdown(
        """
        - The study is **observational**, so associations should not be interpreted as causal effects.
        - Height and weight data are incomplete, particularly for older competitions.
        - Physical characteristics may not represent measurements taken at the exact date of competition.
        - Athlete observations are repeated across years and rounds, requiring repeated-measures methods.
        - Final time is mathematically determined by the first and second 50 m splits, so using both splits to predict final time would create **target leakage**.
        """
    )
