from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

OUTPUT_FILE = ROOT / "data" / "wattguard_output.csv"
EVALUATION_FILE = ROOT / "data" / "wattguard_evaluation.csv"
FULL_FILE = ROOT / "notebooks" / "full.csv"
DESTINATION = ROOT / "data" / "wattguard_web_history.csv.gz"

DAYS = 90


def parse_source_id(value):
    value = str(value)

    if value.startswith("WG-"):
        try:
            return int(
                value.replace(
                    "WG-",
                    "",
                )
            )
        except Exception:
            return np.nan

    return np.nan


print("Loading WattGuard output...")
output = pd.read_csv(
    OUTPUT_FILE
)

print("Loading evaluation mapping...")
evaluation = pd.read_csv(
    EVALUATION_FILE
)

print("Loading SGCC full.csv...")
full = pd.read_csv(
    FULL_FILE
)

if len(output) != len(evaluation):
    raise ValueError(
        "wattguard_output.csv and wattguard_evaluation.csv "
        "must have the same number of rows for this exporter."
    )

# Confirm row alignment using numeric features before trusting it.
shared_checks = [
    c for c in [
        "Risk_Score",
        "Priority_Score",
        "Estimated_Unbilled_Units",
        "mean_usage",
        "max_usage",
        "std_usage",
        "zero_ratio",
    ]
    if c in output.columns
    and c in evaluation.columns
]

scores = []

for col in shared_checks:
    a = pd.to_numeric(
        output[col],
        errors="coerce",
    )
    b = pd.to_numeric(
        evaluation[col],
        errors="coerce",
    )

    valid = (
        a.notna()
        & b.notna()
    )

    if valid.any():
        close = np.isclose(
            a[valid].to_numpy(),
            b[valid].to_numpy(),
            rtol=1e-7,
            atol=1e-7,
        )

        scores.append(
            float(
                close.mean()
            )
        )

if not scores or np.mean(scores) < 0.98:
    raise ValueError(
        "Could not safely verify row alignment between "
        "output and evaluation files."
    )

source_index = (
    evaluation[
        "Consumer_ID"
    ]
    .map(
        parse_source_id
    )
)

if source_index.isna().any():
    raise ValueError(
        "Some evaluation Consumer_ID values are not WG-xxxxx IDs."
    )

# Identify date columns once.
date_columns = []

for column in full.columns:
    parsed = pd.to_datetime(
        column,
        errors="coerce",
    )

    if not pd.isna(
        parsed
    ):
        date_columns.append(
            (
                column,
                parsed,
            )
        )

date_columns = sorted(
    date_columns,
    key=lambda x: x[1],
)

if len(date_columns) < DAYS:
    raise ValueError(
        f"Only {len(date_columns)} date columns found; "
        f"need at least {DAYS}."
    )

date_columns = date_columns[
    -DAYS:
]

records = []

print(
    f"Exporting last {DAYS} days for "
    f"{len(output):,} WattGuard consumers..."
)

for row_number in range(
    len(output)
):
    consumer_id = str(
        output.iloc[
            row_number
        ][
            "Consumer_ID"
        ]
    )

    source = int(
        source_index.iloc[
            row_number
        ]
    )

    if source not in full.index:
        continue

    raw = full.loc[
        source
    ]

    for column, date_value in date_columns:
        usage = pd.to_numeric(
            raw[column],
            errors="coerce",
        )

        if pd.isna(
            usage
        ):
            continue

        records.append(
            {
                "Consumer_ID": consumer_id,
                "Date": date_value.strftime(
                    "%Y-%m-%d"
                ),
                "Usage": float(
                    usage
                ),
            }
        )

history = pd.DataFrame(
    records
)

history.to_csv(
    DESTINATION,
    index=False,
    compression="gzip",
)

size_mb = (
    DESTINATION.stat().st_size
    / 1024
    / 1024
)

print()
print(
    f"Created: {DESTINATION}"
)
print(
    f"Rows: {len(history):,}"
)
print(
    f"Compressed size: {size_mb:.2f} MB"
)
print()
print(
    "Now commit data/wattguard_web_history.csv.gz "
    "to GitHub. Do NOT commit notebooks/full.csv."
)
