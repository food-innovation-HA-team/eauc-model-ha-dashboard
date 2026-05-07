"""
mapping.py

Maps recipe ingredients to Agribalyse products using the tidy dataframe.
"""

import pandas as pd
from difflib import get_close_matches
from src.config import INGREDIENTS_FILE

PRODUCT_NAME_COL = "Product Name in English"


# ---------------------------------------------------------------------------
# LOAD INGREDIENTS
# ---------------------------------------------------------------------------

def load_ingredients():
    return pd.read_csv(INGREDIENTS_FILE)


# ---------------------------------------------------------------------------
# MATCHING FUNCTIONS
# ---------------------------------------------------------------------------

def exact_match(name, agb_df):
    if PRODUCT_NAME_COL not in agb_df.columns:
        raise KeyError(
            f"Column '{PRODUCT_NAME_COL}' not found. "
            f"Available: {list(agb_df.columns)}"
        )

    matches = agb_df[agb_df[PRODUCT_NAME_COL] == name]
    return matches if len(matches) > 0 else None


def fuzzy_match(name, df, n=5, cutoff=0.6):
    # Ensure all names are strings and drop NaN
    all_names = (
        df[PRODUCT_NAME_COL]
        .dropna()
        .astype(str)
        .tolist()
    )

    name = str(name)  # ensure input is also a string

    return get_close_matches(name, all_names, n=n, cutoff=cutoff)


# ---------------------------------------------------------------------------
# MAIN MAPPING FUNCTION
# ---------------------------------------------------------------------------

def map_ingredients_to_agribalyse(df_ing, df_agb_tidy):
    mapped_frames = []

    for _, row in df_ing.iterrows():
        ing_name = row["ingredient"]
        agb_name = row["agribalyse_name"]

        # --- PRIMARY: exact match ---
        exact = exact_match(agb_name, df_agb_tidy)

        if exact is not None:
            matched = exact

        else:
            # --- SECONDARY: fuzzy match ---
            suggestions = fuzzy_match(agb_name, df_agb_tidy)

            if suggestions:
                best = suggestions[0]
                matched = df_agb_tidy[df_agb_tidy[PRODUCT_NAME_COL] == best]

            else:
                # --- FALLBACK: try first word only ---
                fallback = ing_name.split()[0]   # e.g. "Tomato peeled or chopped" → "Tomato"
                fallback_matches = df_agb_tidy[
                    df_agb_tidy[PRODUCT_NAME_COL]
                    .str.contains(fallback, case=False, na=False)
                ]

                if not fallback_matches.empty:
                    matched = fallback_matches.iloc[0:1]  # keep as DataFrame slice
                else:
                    # --- NO MATCH FOUND ANYWHERE ---
                    raise ValueError(
                        f"No match found for ingredient '{ing_name}' "
                        f"with search term '{agb_name}' or fallback '{fallback}'."
                    )

        # -------------------------------------------------------------------
        # ADD ORIGINAL INGREDIENT + CLEANED QUANTITY
        # -------------------------------------------------------------------
        matched = matched.copy()
        matched["ingredient"] = ing_name

        # Clean and convert quantity_g
        qty_raw = str(row["quantity_g"])
        qty_clean = qty_raw.replace("g", "").strip()
        qty = pd.to_numeric(qty_clean, errors="coerce")
        if pd.isna(qty):
            qty = 0.0

        matched["quantity_g"] = qty

        mapped_frames.append(matched)

    return pd.concat(mapped_frames, ignore_index=True)
