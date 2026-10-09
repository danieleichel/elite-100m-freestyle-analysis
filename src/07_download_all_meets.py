import requests
from importlib import import_module


headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Origin": "https://www.worldaquatics.com",
    "Referer": "https://www.worldaquatics.com"
}


competition_module = import_module("00_competition_list")
competitions = competition_module.competitions


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


def find_100_free_events(competition_id):

    data = get_events(competition_id)

    events = {}

    for sport in data.get("Sports", []):

        if sport.get("Code") != "SW":
            continue

        for event in sport.get("DisciplineList", []):

            name = event.get("DisciplineName", "")

            if name == "Men's 100m Freestyle":
                events["men"] = event.get("Id")

            elif name == "Women's 100m Freestyle":
                events["women"] = event.get("Id")

    return events


# Test only Singapore 2025 first
competition_id = "4725"

events = find_100_free_events(competition_id)

print("Singapore 2025")
print(events)
