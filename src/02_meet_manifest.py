import pandas as pd
from pathlib import Path
from importlib import import_module


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


# Load competition list
competition_module = import_module("00_competition_list")
competitions = competition_module.competitions


# Convert competition list to DataFrame
meet_df = pd.DataFrame(competitions)


# Create unique meet ID
meet_df["meet_id"] = (
    meet_df["year"].astype(str)
    + "_"
    + meet_df["meet_type"]
    .str.lower()
        .str.replace(" ", "_")
)


# Add pool length
meet_df["pool_length_m"] = 50


# Save meet manifest
output_file = RAW_DATA_DIR / "meet_manifest.csv"

meet_df.to_csv(output_file, index=False)


print(f"Meet manifest created: {output_file}")
print(f"Number of meets: {len(meet_df)}")

print("\nMeet counts by type:")
print(meet_df["meet_type"].value_counts())
