import requests
import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MEN_DIR = PROJECT_ROOT / "data" / "raw" / "men"
WOMEN_DIR = PROJECT_ROOT / "data" / "raw" / "women"

MEN_DIR.mkdir(parents=True, exist_ok=True)
WOMEN_DIR.mkdir(parents=True, exist_ok=True)


EVENTS = {
    "men": {
        "event_id": "103eb1a8-4636-4cae-b258-faf9b7339deb",
        "output": MEN_DIR / "singapore_2025_100_free.csv"
    },
    "women": {
        "event_id": "8ffdb6b8-9fed-432d-ad89-f3f2a9add412",
        "output": WOMEN_DIR / "singapore_2025_100_free.csv"
    }
}


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


def parse_results(data, sex):

    rows = []

    for race_unit in data.get("Heats", []):

        phase = race_unit.get("PhaseName")

        # Ignore summary tables
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

            row = {
                "meet_name": "2025 World Championships",
                "meet_type": "World Championships",
                "competition_year": 2025,
                "location": "Singapore",
                "race_round": phase,
                "sex": sex,

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
            }

            rows.append(row)

    return pd.DataFrame(rows)


for sex, info in EVENTS.items():

    print(f"\nDownloading {sex}...")

    data = get_event_data(info["event_id"])

    df = parse_results(data, sex)

    df.to_csv(
        info["output"],
        index=False
    )

    print(f"Rows saved: {len(df)}")
    print(f"Saved to: {info['output']}")
