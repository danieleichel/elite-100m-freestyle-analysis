import requests
import pandas as pd
from pathlib import Path
import time


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EVENT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "major_meet_event_ids.csv"
)

MEN_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "men"
    / "all_major_meets_100_free.csv"
)

WOMEN_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "women"
    / "all_major_meets_100_free.csv"
)


headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Origin": "https://www.worldaquatics.com",
    "Referer": "https://www.worldaquatics.com"
}


def get_event_data(event_id):

    url = f"https://api.worldaquatics.com/fina/events/{event_id}"

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def parse_event(data, meet, sex):

    rows = []

    for race_unit in data.get("Heats", []):

        phase = race_unit.get("PhaseName")

        if phase == "Summary":
            continue

        results = race_unit.get("Results", [])

        for result in results:

            splits = result.get("Splits", [])

            first_50 = None
            second_50 = None

            if len(splits) >= 1:
                first_50 = splits[0].get("Time")

            if len(splits) >= 2:
                second_50 = splits[1].get("DifferentialTime")

            rows.append({
                "competition_id": meet["competition_id"],
                "meet_name": meet["meet_name"],
                "competition_year": meet["year"],
                "city": meet["city"],
                "country": meet["country"],
                "sex": sex,
                "race_round": phase,

                "swimmer_id": result.get("PersonId"),
                "swimmer_name": result.get("FullName"),
                "represented_country": result.get("NAT"),
                "age": result.get("AthleteResultAge"),

                "lane": result.get("Lane"),
                "place": result.get("Rank"),
                "heat_place": result.get("HeatRank"),

                "reaction_time": result.get("RT"),
                "first_50": first_50,
                "second_50": second_50,
                "final_time": result.get("Time")
            })

    return rows


meets = pd.read_csv(EVENT_FILE)

men_rows = []
women_rows = []


for _, meet in meets.iterrows():

    print()
    print(
        f"{int(meet['year'])} - "
        f"{meet['meet_name']}"
    )

    # MEN
    men_event_id = meet["men_100_free_event_id"]

    print("Downloading men...")

    try:
        men_data = get_event_data(men_event_id)

        rows = parse_event(
            men_data,
            meet,
            "Men"
        )

        men_rows.extend(rows)

        print(f"Men rows added: {len(rows)}")

    except Exception as error:
        print(f"Men error: {error}")

    time.sleep(0.25)

    # WOMEN
    women_event_id = meet["women_100_free_event_id"]

    print("Downloading women...")

    try:
        women_data = get_event_data(women_event_id)

        rows = parse_event(
            women_data,
            meet,
            "Women"
        )

        women_rows.extend(rows)

        print(f"Women rows added: {len(rows)}")

    except Exception as error:
        print(f"Women error: {error}")

    time.sleep(0.25)


men_df = pd.DataFrame(men_rows)
women_df = pd.DataFrame(women_rows)


men_df.to_csv(
    MEN_OUTPUT,
    index=False
)

women_df.to_csv(
    WOMEN_OUTPUT,
    index=False
)


print()
print("=" * 60)

print(f"Total men's rows: {len(men_df)}")
print(f"Total women's rows: {len(women_df)}")

print()
print(f"Men saved to: {MEN_OUTPUT}")
print(f"Women saved to: {WOMEN_OUTPUT}")
