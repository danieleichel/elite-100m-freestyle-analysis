import pandas as pd
from pathlib import Path
from importlib import import_module


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

competition_module = import_module("00_competition_list")
competitions = competition_module.competitions


# Raw dataset structure
columns = [
    "meet_id",
    "meet_name",
    "meet_type",
    "meet_start_date",
    "meet_end_date",
    "city",
    "country",
    "pool_length_m",
    "event",
    "race_round",
    "heat_number",
    "lane",
    "place",

    "swimmer_id",
    "swimmer_name",
    "sex",
    "represented_country",
    "birth_country",
    "age",
    "height_cm",

    "reaction_time",
    "first_50",
    "second_50",
    "final_time",

    "stroke_rate_1",
    "stroke_rate_2",
    "stroke_length_1",
    "stroke_length_2",

    "underwater_start_m",
    "underwater_turn_m",
    "underwater_start_time",
    "underwater_turn_time",

    "source_url",
    "data_quality_flag",
]


# Create empty template
df = pd.DataFrame(columns=columns)


# Save template
output_file = RAW_DATA_DIR / "swimming_raw_template.csv"
df.to_csv(output_file, index=False)

print(f"Template created: {output_file}")
print(f"Number of variables: {len(columns)}")
print(f"Competitions loaded: {len(competitions)}")
