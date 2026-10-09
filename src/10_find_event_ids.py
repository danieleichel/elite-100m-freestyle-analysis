import requests
import pandas as pd
from pathlib import Path
import time


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "major_meet_ids.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "major_meet_event_ids.csv"
)


headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Origin": "https://www.worldaquatics.com",
    "Referer": "https://www.worldaquatics.com"
}


def get_events(competition_id):

    url = (
        f"https://api.worldaquatics.com/fina/"
        f"competitions/{competition_id}/events"
    )

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def find_100_free_events(data):

    men_event_id = None
    women_event_id = None

    for sport in data.get("Sports", []):

        if sport.get("Code") != "SW":
            continue

        for event in sport.get("DisciplineList", []):

            event_name = event.get("DisciplineName", "")

            if event_name == "Men's 100m Freestyle":
                men_event_id = event.get("Id")

            elif event_name == "Women's 100m Freestyle":
                women_event_id = event.get("Id")

    return men_event_id, women_event_id


meets = pd.read_csv(INPUT_FILE)

rows = []


for _, meet in meets.iterrows():

    competition_id = int(meet["competition_id"])

    print()
    print(
        f"Checking {meet['year']} - "
        f"{meet['name']}"
    )

    try:

        data = get_events(competition_id)

        men_id, women_id = find_100_free_events(data)

        print(f"Men:   {men_id}")
        print(f"Women: {women_id}")

        rows.append({
            "year": meet["year"],
            "competition_id": competition_id,
            "meet_name": meet["name"],
            "city": meet["city"],
            "country": meet["country"],
            "men_100_free_event_id": men_id,
            "women_100_free_event_id": women_id
        })

    except Exception as error:

        print(f"ERROR: {error}")

        rows.append({
            "year": meet["year"],
            "competition_id": competition_id,
            "meet_name": meet["name"],
            "city": meet["city"],
            "country": meet["country"],
            "men_100_free_event_id": None,
            "women_100_free_event_id": None
        })

    time.sleep(0.25)


event_df = pd.DataFrame(rows)

event_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("=" * 60)

print(f"Meets checked: {len(event_df)}")

print(
    "Men's events found:",
    event_df["men_100_free_event_id"].notna().sum()
)

print(
    "Women's events found:",
    event_df["women_100_free_event_id"].notna().sum()
)

print()
print("Missing event IDs:")

missing = event_df[
    event_df[
        [
            "men_100_free_event_id",
            "women_100_free_event_id"
        ]
    ].isna().any(axis=1)
]

if len(missing) == 0:
    print("None")
else:
    print(
        missing[
            [
                "year",
                "meet_name",
                "men_100_free_event_id",
                "women_100_free_event_id"
            ]
        ].to_string(index=False)
    )

print()
print(f"Saved: {OUTPUT_FILE}")
