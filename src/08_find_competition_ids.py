import requests
import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "competition_ids.csv"


headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Origin": "https://www.worldaquatics.com",
    "Referer": "https://www.worldaquatics.com"
}


TARGET_YEARS = range(2000, 2026)


def get_competitions_for_year(year):
    all_competitions = []

    date_from = f"{year}-01-01T00:00:00+00:00"
    date_to = f"{year + 1}-01-01T00:00:00+00:00"

    page = 0

    while True:
        url = "https://api.worldaquatics.com/fina/competitions"

        params = {
            "pageSize": 100,
            "venueDateFrom": date_from,
            "venueDateTo": date_to,
            "disciplines": "",
            "group": "FINA",
            "sort": "dateFrom,asc",
            "page": page
        }

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        all_competitions.extend(
            data.get("content", [])
        )

        page_info = data.get("pageInfo", {})
        num_pages = page_info.get("numPages", 1)

        if page >= num_pages - 1:
            break

        page += 1

    return all_competitions


rows = []


for year in TARGET_YEARS:

    print(f"Checking {year}...")

    competitions = get_competitions_for_year(year)

    print(f"Competitions found: {len(competitions)}")

    for competition in competitions:

        disciplines = competition.get("disciplines", [])

        if "SW" not in disciplines:
            continue

        location = competition.get("location") or {}

        rows.append({
            "year": year,
            "competition_id": competition.get("id"),
            "name": competition.get("name"),
            "city": location.get("city"),
            "country": location.get("countryName"),
            "disciplines": ", ".join(disciplines),
            "date_from": (
                competition.get("dateFrom") or ""
            )[:10],
            "date_to": (
                competition.get("dateTo") or ""
            )[:10]
        })


df = pd.DataFrame(rows)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print(f"Saved: {OUTPUT_FILE}")
print(f"Swimming competitions found: {len(df)}")

print()
print(df.head(30).to_string(index=False))
