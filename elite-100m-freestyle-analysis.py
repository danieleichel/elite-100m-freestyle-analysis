import pandas as pd
from pathlib import Path


# Define project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


# Define the raw dataset structure
columns = [
    "race_id",
    "swimmer_id",
    "swimmer_name",
    "competition",
    "competition_year",
    "race_round",
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
]


# Create an empty DataFrame
df = pd.DataFrame(columns=columns)


# Save template
output_file = RAW_DATA_DIR / "swimming_raw_template.csv"
df.to_csv(output_file, index=False)

print(f"Template created: {output_file}")
print(f"Number of variables: {len(columns)}")
