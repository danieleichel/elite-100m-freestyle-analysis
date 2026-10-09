import requests


COMPETITION_ID = "4725"

url = (
    f"https://api.worldaquatics.com/fina/"
    f"competitions/{COMPETITION_ID}/events"
)

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Origin": "https://www.worldaquatics.com",
    "Referer": "https://www.worldaquatics.com",
}


response = requests.get(
    url,
    headers=headers,
    timeout=30
)

response.raise_for_status()

data = response.json()


print("Connection successful.")
print()


for sport in data.get("Sports", []):

    if sport.get("Code") != "SW":
        continue

    for event in sport.get("DisciplineList", []):

        event_name = event.get("DisciplineName", "")

        if event_name in [ "Men's 100m Freestyle", "Women's 100m Freestyle"]:

            print(
                "Event:",
                event_name
            )

            print(
                "Gender:",
                event.get("Gender")
            )

            print(
                "Event ID:",
                event.get("Id")
            )

            print("-" * 50)
