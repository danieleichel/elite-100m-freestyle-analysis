import time
from pathlib import Path

import pandas as pd
import requests


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
)

MEN_OUTPUT = (
    RAW_DIR
    / "men"
    / "all_major_meets_100_free.csv"
)

WOMEN_OUTPUT = (
    RAW_DIR
    / "women"
    / "all_major_meets_100_free.csv"
)

EVENT_MANIFEST_OUTPUT = (
    RAW_DIR
    / "major_meet_event_ids.csv"
)


# ============================================================
# WORLD AQUATICS API
# ============================================================

BASE_URL = "https://api.worldaquatics.com/fina"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Origin": "https://www.worldaquatics.com",
    "Referer": "https://www.worldaquatics.com"
}

REQUEST_DELAY = 0.25
REQUEST_TIMEOUT = 30


# ============================================================
# FIXED STUDY MANIFEST
# ============================================================
#
# Senior long-course Olympic Games and World Championships
# from 2000 through 2025.
#
# Event IDs correspond to the men's and women's 100 m
# freestyle events in the World Aquatics API.
#
# ============================================================

MEETS = [
    {
        "year": 2000,
        "competition_id": 888,
        "meet_name": "Olympic Games Sydney 2000",
        "city": "Sydney",
        "country": "Australia",
        "men_100_free_event_id": "f1bc54a7-a8f0-4638-b00b-dbadeb7dc7ea",
        "women_100_free_event_id": "189c5443-06ab-4b85-b8de-3a3a6b819fe8"
    },
    {
        "year": 2001,
        "competition_id": 865,
        "meet_name": "9th FINA World Championships 2001",
        "city": "Fukuoka",
        "country": "Japan",
        "men_100_free_event_id": "66ab6d23-6a17-4157-9f9a-7c84f5bd5b8a",
        "women_100_free_event_id": "c351575b-37c1-4854-8400-c126d06c05c6"
    },
    {
        "year": 2003,
        "competition_id": 816,
        "meet_name": "10th FINA World Championships 2003",
        "city": "Barcelona",
        "country": "Spain",
        "men_100_free_event_id": "0138e0a1-0468-4645-8154-6e373afa4105",
        "women_100_free_event_id": "381634f2-960f-4816-b6aa-a47c5b008009"
    },
    {
        "year": 2004,
        "competition_id": 792,
        "meet_name": "Olympic Games Athens 2004",
        "city": "Athens",
        "country": "Greece",
        "men_100_free_event_id": "247ecdc1-1618-483a-b466-402de07b2da7",
        "women_100_free_event_id": "81081d58-bee3-495a-8905-b3d8d56f7eae"
    },
    {
        "year": 2005,
        "competition_id": 771,
        "meet_name": "11th FINA World Championships 2005",
        "city": "Montreal",
        "country": "Canada",
        "men_100_free_event_id": "c2c3cfec-b8b6-4cbb-8ab2-007c4dbe39e1",
        "women_100_free_event_id": "9df86cb8-19e6-41f4-b768-ab32c4faa8e8"
    },
    {
        "year": 2007,
        "competition_id": 734,
        "meet_name": "12th FINA World Championships 2007",
        "city": "Melbourne",
        "country": "Australia",
        "men_100_free_event_id": "b7668553-8665-42ea-aa0e-5b042d2abd17",
        "women_100_free_event_id": "d8866523-74b3-4754-a28e-22210280ff50"
    },
    {
        "year": 2008,
        "competition_id": 657,
        "meet_name": "Olympic Games Beijing 2008",
        "city": "Beijing",
        "country": "People's Republic of China",
        "men_100_free_event_id": "adab28e8-b754-4a67-b9ea-9ceb365b9fb9",
        "women_100_free_event_id": "f640b682-83a3-4125-89a1-63307d70b961"
    },
    {
        "year": 2009,
        "competition_id": 618,
        "meet_name": "13th FINA World Championships 2009",
        "city": "Rome",
        "country": "Italy",
        "men_100_free_event_id": "c014ddd5-e847-447f-a1bb-95385ce5f80d",
        "women_100_free_event_id": "9fd8a9f9-588d-41ec-bf00-c82fbdca04cc"
    },
    {
        "year": 2011,
        "competition_id": 517,
        "meet_name": "14th FINA World Championships 2011",
        "city": "Shanghai",
        "country": "People's Republic of China",
        "men_100_free_event_id": "74843ec2-bbc8-43d1-ae10-d10e9b2959be",
        "women_100_free_event_id": "e44eb050-d47c-4a53-af09-bb2a34c9ac0b"
    },
    {
        "year": 2012,
        "competition_id": 468,
        "meet_name": "Olympic Games London 2012",
        "city": "London",
        "country": "Great Britain",
        "men_100_free_event_id": "ef25ec47-7ba0-40ab-aa1e-b079501f524a",
        "women_100_free_event_id": "1edf92f0-3581-4d36-b44a-ea20bcff3a9b"
    },
    {
        "year": 2013,
        "competition_id": 416,
        "meet_name": "15th FINA World Championships 2013",
        "city": "Barcelona",
        "country": "Spain",
        "men_100_free_event_id": "479cc0ca-d2ef-46b1-804e-eda8b0c1f846",
        "women_100_free_event_id": "c21dab62-64a1-4b70-be80-d0bc058e8bfe"
    },
    {
        "year": 2015,
        "competition_id": 312,
        "meet_name": "16th FINA World Championships 2015",
        "city": "Kazan",
        "country": "Russian Federation",
        "men_100_free_event_id": "750199e3-e73a-4256-9417-00da08247d37",
        "women_100_free_event_id": "cec23d54-8d08-464f-aa40-79937dc8d1ba"
    },
    {
        "year": 2016,
        "competition_id": 262,
        "meet_name": "Olympic Games Rio 2016",
        "city": "Rio de Janeiro",
        "country": "Brazil",
        "men_100_free_event_id": "8da7743a-4aa1-4fd0-bbbf-3ac82e937dea",
        "women_100_free_event_id": "c1ef33bc-85c8-4f9e-bc04-ca09843f8851"
    },
    {
        "year": 2017,
        "competition_id": 213,
        "meet_name": "17th FINA World Championships 2017",
        "city": "Budapest",
        "country": "Hungary",
        "men_100_free_event_id": "5fed15b6-d2ac-4f5b-b27c-339dcf0da3c8",
        "women_100_free_event_id": "acf7d9bf-ad7c-4fa1-bdc1-8fa2317651b6"
    },
    {
        "year": 2019,
        "competition_id": 95,
        "meet_name": "18th FINA World Championships 2019",
        "city": "Gwangju",
        "country": "Republic of Korea",
        "men_100_free_event_id": "b4fb82fc-5080-47e3-9761-677f3d593e67",
        "women_100_free_event_id": "f69df3c8-3953-467f-8029-cb4141f6d39b"
    },
    {
        "year": 2021,
        "competition_id": 5,
        "meet_name": "Olympic Games Tokyo 2020",
        "city": "Tokyo",
        "country": "Japan",
        "men_100_free_event_id": "cc344f88-0bc1-4dc8-be43-68344ee9c665",
        "women_100_free_event_id": "c86a3fdf-1c2a-4c4c-bcfb-30cffebf9289"
    },
    {
        "year": 2022,
        "competition_id": 2902,
        "meet_name": "19th FINA World Championships Budapest 2022",
        "city": "Budapest",
        "country": "Hungary",
        "men_100_free_event_id": "3da7b4cd-1453-4b63-a3d5-c66ef685e82a",
        "women_100_free_event_id": "7d753e0f-29ff-47cf-a305-e4e59bb7930b"
    },
    {
        "year": 2023,
        "competition_id": 1,
        "meet_name": "World Aquatics Championships - Fukuoka 2023",
        "city": "Fukuoka",
        "country": "Japan",
        "men_100_free_event_id": "33a7e0f5-5b4c-4280-8c20-05bcd774fe73",
        "women_100_free_event_id": "67c7ccf7-44c5-4c9e-92cd-2cf7887e6628"
    },
    {
        "year": 2024,
        "competition_id": 2969,
        "meet_name": "World Aquatics Championships - Doha 2024",
        "city": "Doha",
        "country": "Qatar",
        "men_100_free_event_id": "28b77ca7-d106-47f6-a06a-aee09c779c5d",
        "women_100_free_event_id": "1cefc9ab-ac60-4e83-a820-003e9e814dc8"
    },
    {
        "year": 2024,
        "competition_id": 2943,
        "meet_name": "Olympic Games Paris 2024",
        "city": "Paris",
        "country": "France",
        "men_100_free_event_id": "80fa896e-b6e3-4087-9743-26eff6ef8a3f",
        "women_100_free_event_id": "f4a7ea40-3136-4687-a43b-91344071a74d"
    },
    {
        "year": 2025,
        "competition_id": 4725,
        "meet_name": "World Aquatics Championships - Singapore 2025",
        "city": "Singapore",
        "country": "Singapore",
        "men_100_free_event_id": "103eb1a8-4636-4cae-b258-faf9b7339deb",
        "women_100_free_event_id": "8ffdb6b8-9fed-432d-ad89-f3f2a9add412"
    }
]


# ============================================================
# API REQUEST
# ============================================================

def get_event_data(event_id):

    url = (
        f"{BASE_URL}/events/{event_id}"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# PARSE WORLD AQUATICS EVENT
# ============================================================

def parse_event(
    data,
    meet,
    sex
):

    rows = []

    for race_unit in data.get(
        "Heats",
        []
    ):

        phase = race_unit.get(
            "PhaseName"
        )

        if phase == "Summary":
            continue

        results = race_unit.get(
            "Results",
            []
        )

        for result in results:

            splits = result.get(
                "Splits",
                []
            )

            first_50 = None
            second_50 = None

            if len(splits) >= 1:

                first_50 = (
                    splits[0]
                    .get("Time")
                )

            if len(splits) >= 2:

                second_50 = (
                    splits[1]
                    .get(
                        "DifferentialTime"
                    )
                )

            rows.append(
                {
                    "competition_id":
                        meet[
                            "competition_id"
                        ],

                    "meet_name":
                        meet[
                            "meet_name"
                        ],

                    "competition_year":
                        meet[
                            "year"
                        ],

                    "city":
                        meet[
                            "city"
                        ],

                    "country":
                        meet[
                            "country"
                        ],

                    "sex":
                        sex,

                    "race_round":
                        phase,

                    "swimmer_id":
                        result.get(
                            "PersonId"
                        ),

                    "swimmer_name":
                        result.get(
                            "FullName"
                        ),

                    "represented_country":
                        result.get(
                            "NAT"
                        ),

                    "age":
                        result.get(
                            "AthleteResultAge"
                        ),

                    "lane":
                        result.get(
                            "Lane"
                        ),

                    "place":
                        result.get(
                            "Rank"
                        ),

                    "heat_place":
                        result.get(
                            "HeatRank"
                        ),

                    "reaction_time":
                        result.get(
                            "RT"
                        ),

                    "first_50":
                        first_50,

                    "second_50":
                        second_50,

                    "final_time":
                        result.get(
                            "Time"
                        )
                }
            )

    return rows


# ============================================================
# DOWNLOAD EVENT
# ============================================================

def download_event(
    meet,
    sex,
    event_id
):

    print(
        f"Downloading {sex.lower()}..."
    )

    data = get_event_data(
        event_id
    )

    rows = parse_event(
        data,
        meet,
        sex
    )

    print(
        f"{sex} rows added: "
        f"{len(rows)}"
    )

    time.sleep(
        REQUEST_DELAY
    )

    return rows


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Create output directories
    # --------------------------------------------------------

    MEN_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    WOMEN_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    EVENT_MANIFEST_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Save canonical study manifest
    # --------------------------------------------------------

    meet_df = pd.DataFrame(
        MEETS
    )

    meet_df.to_csv(
        EVENT_MANIFEST_OUTPUT,
        index=False
    )

    print(
        "=" * 80
    )

    print(
        "ELITE 100 M FREESTYLE DATA COLLECTION"
    )

    print(
        "=" * 80
    )

    print(
        f"Meets in study manifest: "
        f"{len(meet_df)}"
    )

    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    men_rows = []
    women_rows = []

    failures = []

    for meet in MEETS:

        print()

        print(
            "=" * 80
        )

        print(
            f"{meet['year']} - "
            f"{meet['meet_name']}"
        )

        print(
            "=" * 80
        )

        # MEN

        try:

            rows = download_event(
                meet,
                "Men",
                meet[
                    "men_100_free_event_id"
                ]
            )

            men_rows.extend(
                rows
            )

        except Exception as error:

            print(
                f"Men error: {error}"
            )

            failures.append(
                {
                    "year":
                        meet["year"],

                    "meet_name":
                        meet["meet_name"],

                    "sex":
                        "Men",

                    "error":
                        str(error)
                }
            )

        # WOMEN

        try:

            rows = download_event(
                meet,
                "Women",
                meet[
                    "women_100_free_event_id"
                ]
            )

            women_rows.extend(
                rows
            )

        except Exception as error:

            print(
                f"Women error: {error}"
            )

            failures.append(
                {
                    "year":
                        meet["year"],

                    "meet_name":
                        meet["meet_name"],

                    "sex":
                        "Women",

                    "error":
                        str(error)
                }
            )

    # --------------------------------------------------------
    # Convert to DataFrames
    # --------------------------------------------------------

    men_df = pd.DataFrame(
        men_rows
    )

    women_df = pd.DataFrame(
        women_rows
    )

    # --------------------------------------------------------
    # Save raw results
    # --------------------------------------------------------

    men_df.to_csv(
        MEN_OUTPUT,
        index=False
    )

    women_df.to_csv(
        WOMEN_OUTPUT,
        index=False
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    print()
    print(
        "=" * 80
    )

    print(
        "DATA COLLECTION COMPLETE"
    )

    print(
        "=" * 80
    )

    print()

    print(
        f"Men rows: "
        f"{len(men_df)}"
    )

    print(
        f"Men unique swimmers: "
        f"{men_df['swimmer_id'].nunique()}"
    )

    print()

    print(
        f"Women rows: "
        f"{len(women_df)}"
    )

    print(
        f"Women unique swimmers: "
        f"{women_df['swimmer_id'].nunique()}"
    )

    print()

    print(
        f"Failed downloads: "
        f"{len(failures)}"
    )

    if failures:

        print()

        print(
            "FAILED DOWNLOADS"
        )

        for failure in failures:

            print(
                f"{failure['year']} - "
                f"{failure['meet_name']} - "
                f"{failure['sex']}: "
                f"{failure['error']}"
            )

    print()

    print(
        "Saved:"
    )

    print(
        EVENT_MANIFEST_OUTPUT
    )

    print(
        MEN_OUTPUT
    )

    print(
        WOMEN_OUTPUT
    )


if __name__ == "__main__":
    main()
