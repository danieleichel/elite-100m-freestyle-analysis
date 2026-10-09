import pandas as pd
import requests
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path


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

MASTER_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "athlete_master.csv"
)

CANDIDATE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "wikidata_physical_candidates.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "athlete_master_physical_clean.csv"
)


# ============================================================
# NAME FUNCTIONS
# ============================================================

def normalize_name(text):

    if pd.isna(text):
        return ""

    text = str(text).lower()

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = "".join(
        char
        for char in text
        if not unicodedata.combining(char)
    )

    for char in [
        "'",
        "-",
        ".",
        ","
    ]:
        text = text.replace(
            char,
            " "
        )

    return " ".join(
        text.split()
    )


def token_sort_name(text):

    tokens = normalize_name(
        text
    ).split()

    return " ".join(
        sorted(tokens)
    )


def name_similarity(name1, name2):

    return SequenceMatcher(
        None,
        token_sort_name(name1),
        token_sort_name(name2)
    ).ratio()


# ============================================================
# STEP 1
# BUILD ATHLETE MASTER
# ============================================================

print("=" * 80)
print("STEP 1 - BUILD ATHLETE MASTER")
print("=" * 80)


men = pd.read_csv(
    MEN_FILE
)

women = pd.read_csv(
    WOMEN_FILE
)


if "primary_elite_sample" in men.columns:

    men = men[
        men["primary_elite_sample"] == True
    ].copy()


if "primary_elite_sample" in women.columns:

    women = women[
        women["primary_elite_sample"] == True
    ].copy()


men["sex"] = "Men"
women["sex"] = "Women"


combined = pd.concat(
    [men, women],
    ignore_index=True
)


master_columns = [
    "swimmer_id",
    "swimmer_name",
    "sex"
]


for optional_column in [
    "represented_country",
    "birth_country",
    "age"
]:

    if optional_column in combined.columns:
        master_columns.append(
            optional_column
        )


master = (
    combined[
        master_columns
    ]
    .drop_duplicates(
        subset="swimmer_id"
    )
    .sort_values(
        [
            "sex",
            "swimmer_name"
        ]
    )
    .reset_index(
        drop=True
    )
)


master.to_csv(
    MASTER_FILE,
    index=False
)


print(
    f"Unique athletes: "
    f"{len(master)}"
)

print(
    master["sex"].value_counts()
)

print()


# ============================================================
# STEP 2
# DOWNLOAD WIKIDATA SWIMMER DATABASE
# ============================================================

print("=" * 80)
print("STEP 2 - DOWNLOAD WIKIDATA SWIMMER DATABASE")
print("=" * 80)


query = """
SELECT DISTINCT
    ?person
    ?personLabel
    ?dob
    ?height
    ?weight
WHERE {

    ?person wdt:P106 wd:Q10843402 .
    ?person wdt:P569 ?dob .

    OPTIONAL {
        ?person wdt:P2048 ?height .
    }

    OPTIONAL {
        ?person wdt:P2067 ?weight .
    }

    FILTER(
        YEAR(?dob) >= 1970 &&
        YEAR(?dob) <= 2010
    )

    SERVICE wikibase:label {
        bd:serviceParam wikibase:language "en".
    }
}
"""


url = (
    "https://query.wikidata.org/sparql"
)


headers = {
    "Accept":
        "application/sparql-results+json",

    "User-Agent":
        "Elite100FreestyleResearch/1.0"
}


response = requests.get(
    url,
    params={
        "query": query,
        "format": "json"
    },
    headers=headers,
    timeout=120
)

response.raise_for_status()


bindings = (
    response.json()
    ["results"]
    ["bindings"]
)


print(
    f"Wikidata records downloaded: "
    f"{len(bindings)}"
)


wikidata_rows = []


for item in bindings:

    qid = (
        item["person"]["value"]
        .split("/")[-1]
    )

    label = (
        item
        .get(
            "personLabel",
            {}
        )
        .get(
            "value"
        )
    )

    dob = (
        item
        .get(
            "dob",
            {}
        )
        .get(
            "value"
        )
    )

    height = (
        item
        .get(
            "height",
            {}
        )
        .get(
            "value"
        )
    )

    weight = (
        item
        .get(
            "weight",
            {}
        )
        .get(
            "value"
        )
    )

    if height is not None:

        height = float(
            height
        )

        if height < 3:
            height *= 100

    if weight is not None:

        weight = float(
            weight
        )

    wikidata_rows.append({
        "wikidata_qid":
            qid,

        "wikidata_label":
            label,

        "wikidata_dob":
            dob,

        "height_cm":
            height,

        "weight_kg":
            weight
    })


wikidata = pd.DataFrame(
    wikidata_rows
)


# Remove duplicate Wikidata people caused by
# multiple height/weight claims.
wikidata = (
    wikidata
    .sort_values(
        [
            "wikidata_qid",
            "height_cm",
            "weight_kg"
        ]
    )
    .drop_duplicates(
        subset="wikidata_qid",
        keep="first"
    )
    .reset_index(
        drop=True
    )
)


wikidata[
    "token_name"
] = wikidata[
    "wikidata_label"
].apply(
    token_sort_name
)


print()


# ============================================================
# STEP 3
# MATCH ATHLETES
# ============================================================

print("=" * 80)
print("STEP 3 - MATCH ATHLETES")
print("=" * 80)


candidate_records = []


for _, athlete in master.iterrows():

    swimmer_name = athlete[
        "swimmer_name"
    ]

    target_name = token_sort_name(
        swimmer_name
    )

    # --------------------------------------------------------
    # Exact token match first
    # --------------------------------------------------------

    exact = wikidata[
        wikidata[
            "token_name"
        ] == target_name
    ]

    if len(exact) == 1:

        best = exact.iloc[0]

        score = 1.0

        match_type = "exact"

    else:

        # ----------------------------------------------------
        # Fuzzy fallback
        # ----------------------------------------------------

        scores = wikidata[
            "wikidata_label"
        ].apply(
            lambda name:
            name_similarity(
                swimmer_name,
                name
            )
        )

        best_index = (
            scores.idxmax()
        )

        best = wikidata.loc[
            best_index
        ]

        score = float(
            scores.loc[
                best_index
            ]
        )

        if score >= 0.92:

            match_type = (
                "strong_fuzzy"
            )

        elif score >= 0.80:

            match_type = (
                "review"
            )

        else:

            match_type = (
                "no_match"
            )

    candidate_records.append({

        "swimmer_id":
            athlete[
                "swimmer_id"
            ],

        "swimmer_name":
            swimmer_name,

        "sex":
            athlete[
                "sex"
            ],

        "represented_country":
            athlete.get(
                "represented_country",
                pd.NA
            ),

        "wikidata_qid":
            best[
                "wikidata_qid"
            ],

        "wikidata_label":
            best[
                "wikidata_label"
            ],

        "wikidata_dob":
            best[
                "wikidata_dob"
            ],

        "height_cm":
            best[
                "height_cm"
            ],

        "weight_kg":
            best[
                "weight_kg"
            ],

        "name_match_score":
            round(
                score,
                3
            ),

        "match_type":
            match_type
    })


candidates = pd.DataFrame(
    candidate_records
)


candidates.to_csv(
    CANDIDATE_FILE,
    index=False
)


print(
    candidates[
        "match_type"
    ].value_counts()
)

print()


# ============================================================
# STEP 4
# VALIDATE MATCHES
# ============================================================

print("=" * 80)
print("STEP 4 - VALIDATE MATCHES")
print("=" * 80)


candidates[
    "validated_match"
] = False


# Automatic acceptance
candidates.loc[
    candidates[
        "match_type"
    ].isin(
        [
            "exact",
            "strong_fuzzy"
        ]
    ),
    "validated_match"
] = True


# ------------------------------------------------------------
# Matches manually checked during project development
# ------------------------------------------------------------

MANUAL_APPROVED = [
    "MEOLANS Jose",
    "POPOV Alexander",
    "RICHARDS Matthew",
    "SCHOEMAN Roland",
    "TARGETT Matthew",
    "WHITTLE Jacob Henry",
    "MEISSNER Katrin",
    "VELDHUIS Magdalena"
]


candidates.loc[
    candidates[
        "swimmer_name"
    ].isin(
        MANUAL_APPROVED
    ),
    "validated_match"
] = True


# Known incorrect fuzzy match
candidates.loc[
    candidates[
        "swimmer_name"
    ] == "TANG Yi",
    "validated_match"
] = False


# Do not use physical data from rejected matches
candidates.loc[
    ~candidates[
        "validated_match"
    ],
    [
        "height_cm",
        "weight_kg"
    ]
] = pd.NA


print(
    f"Validated matches: "
    f"{candidates['validated_match'].sum()}"
)

print(
    f"Unvalidated: "
    f"{(~candidates['validated_match']).sum()}"
)

print()


# ============================================================
# STEP 5
# MERGE PHYSICAL DATA
# ============================================================

print("=" * 80)
print("STEP 5 - MERGE PHYSICAL DATA")
print("=" * 80)


physical = candidates[[
    "swimmer_id",
    "wikidata_qid",
    "wikidata_label",
    "wikidata_dob",
    "height_cm",
    "weight_kg",
    "validated_match"
]].copy()


enriched = master.merge(
    physical,
    on="swimmer_id",
    how="left",
    validate="one_to_one"
)


enriched[
    "physical_data_source"
] = pd.NA


enriched[
    "physical_data_notes"
] = pd.Series(
    [pd.NA] * len(enriched),
    dtype="object"
)


has_physical = (
    enriched[
        [
            "height_cm",
            "weight_kg"
        ]
    ]
    .notna()
    .any(
        axis=1
    )
)


enriched.loc[
    has_physical,
    "physical_data_source"
] = "Wikidata"


# ============================================================
# STEP 6
# CLEAN PHYSICAL DATA
# ============================================================

print()
print("=" * 80)
print("STEP 6 - PHYSICAL DATA QUALITY CONTROL")
print("=" * 80)


enriched[
    "height_cm_original"
] = enriched[
    "height_cm"
]


enriched[
    "weight_kg_original"
] = enriched[
    "weight_kg"
]


# ------------------------------------------------------------
# Known Wikidata issue found during QC
# ------------------------------------------------------------

duncan_mask = (
    enriched[
        "swimmer_name"
    ] == "SCOTT Duncan"
)


enriched.loc[
    duncan_mask,
    "height_cm"
] = 190.0


enriched.loc[
    duncan_mask,
    "weight_kg"
] = 81.0


enriched.loc[
    duncan_mask,
    "physical_data_notes"
] = (
    "Wikidata weight appeared to contain "
    "a pounds-to-kilograms error. "
    "Corrected to 81 kg; height set to 190 cm."
)


# ------------------------------------------------------------
# Plausibility flags
# ------------------------------------------------------------

enriched[
    "height_flag"
] = False


enriched[
    "weight_flag"
] = False


enriched.loc[
    enriched[
        "height_cm"
    ].notna()
    &
    (
        (
            enriched[
                "height_cm"
            ] < 150
        )
        |
        (
            enriched[
                "height_cm"
            ] > 215
        )
    ),
    "height_flag"
] = True


enriched.loc[
    enriched[
        "weight_kg"
    ].notna()
    &
    (
        (
            enriched[
                "weight_kg"
            ] < 40
        )
        |
        (
            enriched[
                "weight_kg"
            ] > 125
        )
    ),
    "weight_flag"
] = True


# ------------------------------------------------------------
# BMI for QC only
# ------------------------------------------------------------

enriched[
    "bmi"
] = (
    enriched[
        "weight_kg"
    ]
    /
    (
        enriched[
            "height_cm"
        ] / 100
    ) ** 2
)


enriched[
    "bmi_flag"
] = False


enriched.loc[
    enriched[
        "bmi"
    ].notna()
    &
    (
        (
            enriched[
                "bmi"
            ] < 15
        )
        |
        (
            enriched[
                "bmi"
            ] > 35
        )
    ),
    "bmi_flag"
] = True


# ============================================================
# SAVE FINAL DATASET
# ============================================================

enriched.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print(
    f"Total athletes: "
    f"{len(enriched)}"
)

print(
    f"Height available: "
    f"{enriched['height_cm'].notna().sum()}"
)

print(
    f"Weight available: "
    f"{enriched['weight_kg'].notna().sum()}"
)

print()


print("HEIGHT COVERAGE BY SEX:")

height_summary = (
    enriched
    .groupby(
        "sex"
    )
    ["height_cm"]
    .agg(
        athletes="size",
        height_available="count"
    )
)


height_summary[
    "coverage_percent"
] = (
    height_summary[
        "height_available"
    ]
    /
    height_summary[
        "athletes"
    ]
    * 100
)


print(
    height_summary.round(1)
)

print()


print(
    f"Height flags: "
    f"{enriched['height_flag'].sum()}"
)

print(
    f"Weight flags: "
    f"{enriched['weight_flag'].sum()}"
)

print(
    f"BMI flags: "
    f"{enriched['bmi_flag'].sum()}"
)

print()

print("=" * 80)
print("COMPLETE")
print("=" * 80)

print(
    f"Final physical dataset saved to:"
)

print(
    OUTPUT_FILE
)
