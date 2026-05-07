"""
ingest.py

Ingests the Agribalyse master Excel file (English sheet) and reshapes it into a
tidy, analysis-ready dataframe.
"""

import pandas as pd
from pathlib import Path
from .config import AGRIBALYSE_FILE

# ---------------------------------------------------------------------------
# CONSTANTS — EXACTLY AS THEY APPEAR IN YOUR FILE
# ---------------------------------------------------------------------------

SHEET_NAME = "Agribalyse EN"

DESCRIPTOR_COLS = [
    "Code AGB",
    "Code CIQUAL",
    "Feed Group",
    "Food Subgroup",
    "Product Name in English",
    "LCI Name",
    "DQR",
    "Name and code",
]

METADATA_COLS = [
    "DQR \nOverall",
    "P",
    "Shooting",
    "GR",
    "Ter",
]

STAGES = [
    "Agriculture",
    "Transformation",
    "Packaging",
    "Transport",
    "Supermarket and distribution",
    "Consumption",
    "Total",
]

N_STAGES = len(STAGES)
N_IMPACT_CATEGORIES = 20


# ---------------------------------------------------------------------------
# LOAD RAW FILE
# ---------------------------------------------------------------------------

def load_agribalyse():
    """Load the Agribalyse EN sheet with the correct header row."""
    file_path = Path(AGRIBALYSE_FILE)

    df_raw = pd.read_excel(
        file_path,
        sheet_name=SHEET_NAME,
        header=3,          # Excel row 4 is the true header
        engine="openpyxl",
    )

    # Sanity check
    missing = [c for c in DESCRIPTOR_COLS if c not in df_raw.columns]
    if missing:
        raise ValueError(f"Missing descriptor columns: {missing}")

    missing_meta = [c for c in METADATA_COLS if c not in df_raw.columns]
    if missing_meta:
        raise ValueError(f"Missing metadata columns: {missing_meta}")

    return df_raw


# ---------------------------------------------------------------------------
# PARTITION COLUMNS
# ---------------------------------------------------------------------------

def partition_columns(df_raw):
    """Identify descriptor, impact, and metadata columns."""
    all_cols = df_raw.columns.tolist()

    # Impact columns = everything between first stage and first metadata col
    first_impact_idx = all_cols.index(STAGES[0])
    first_meta_idx = all_cols.index(METADATA_COLS[0])

    impact_cols = all_cols[first_impact_idx:first_meta_idx]

    # Partition into 20 blocks of 7
    impact_blocks = [
        impact_cols[i:i + N_STAGES]
        for i in range(0, len(impact_cols), N_STAGES)
    ]

    if len(impact_blocks) != N_IMPACT_CATEGORIES:
        raise ValueError(
            f"Expected {N_IMPACT_CATEGORIES} impact categories, "
            f"found {len(impact_blocks)}"
        )

    return DESCRIPTOR_COLS, impact_blocks, METADATA_COLS


# ---------------------------------------------------------------------------
# RESHAPE TO TIDY
# ---------------------------------------------------------------------------

def reshape_to_tidy(df_raw, descriptor_cols, impact_blocks):
    """Convert wide Agribalyse format into tidy long format."""
    tidy_frames = []

    for idx, block in enumerate(impact_blocks):
        impact_name = f"impact_{idx+1}"

        df_block = (
            df_raw[descriptor_cols + block]
            .melt(
                id_vars=descriptor_cols,
                value_vars=block,
                var_name="stage",
                value_name="value_per_kg",
            )
        )

        df_block["impact_category"] = impact_name
        tidy_frames.append(df_block)

    return pd.concat(tidy_frames, ignore_index=True)


# ---------------------------------------------------------------------------
# PUBLIC PIPELINE
# ---------------------------------------------------------------------------

def load_and_reshape_agribalyse():
    df_raw = load_agribalyse()
    descriptor_cols, impact_blocks, metadata_cols = partition_columns(df_raw)
    df_tidy = reshape_to_tidy(df_raw, descriptor_cols, impact_blocks)
    return df_tidy
