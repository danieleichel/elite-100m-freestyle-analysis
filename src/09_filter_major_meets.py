import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "competition_ids.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "major_meet_ids.csv"
)


df = pd.read_csv(INPUT_FILE)


def is_major_meet(name):

    name = str(name).lower()

    # Senior Olympic Games only
    if (
        "olympic games" in name
        and "youth" not in name
    ):
        return True

    # Senior long-course World Championships
    if (
        (
            "fina world championships" in name
            or "world aquatics championships" in name
        )
        and "25m" not in name
        and "junior" not in name
        and "masters" not in name
    ):
        return True

    return False


major = df[
    df["name"].apply(is_major_meet)
].copy()


major = major.sort_values(
    by=["year", "date_from"]
)


major.to_csv(
    OUTPUT_FILE,
    index=False
)


print(f"Major meets found: {len(major)}")
print()

print(
    major[
        [
            "year",
            "competition_id",
            "name",
            "city",
            "country"
        ]
    ].to_string(index=False)
)

print()
print(f"Saved: {OUTPUT_FILE}")
