"""
baseline.py

Compute baseline environmental impacts for a recipe using the tidy,
mapped Agribalyse dataframe.

Input:
    df_mapped  (from mapping.map_ingredients_to_agribalyse)

Output:
    df_baseline_ingredient  – impacts per ingredient × stage × impact_category
    df_baseline_recipe      – impacts aggregated to recipe level
"""

import pandas as pd


# ---------------------------------------------------------------------------
# 1. Convert g → kg
# ---------------------------------------------------------------------------

def add_quantity_kg(df):
    # Clean and convert quantity_g to numeric
    df = df.copy()
    df["quantity_g"] = (
        df["quantity_g"]
        .astype(str)          # ensure string for cleaning
        .str.replace(r"[^0-9.\-]", "", regex=True)  # remove units, spaces, stray chars
    )
    df["quantity_g"] = pd.to_numeric(df["quantity_g"], errors="coerce")

    # Now safe to divide
    df["quantity_kg"] = df["quantity_g"] / 1000.0

    return df

# ---------------------------------------------------------------------------
# 2. Compute ingredient-level impacts
# ---------------------------------------------------------------------------

def compute_ingredient_impacts(df_mapped):
    """
    For each ingredient × stage × impact_category:
        impact = quantity_kg × value_per_kg
    """
    df = add_quantity_kg(df_mapped)

    df["impact_value"] = df["quantity_kg"] * df["value_per_kg"]

    # Keep only the relevant columns
    cols = [
        "ingredient",
        "quantity_g",
        "quantity_kg",
        "Code AGB",
        "Product Name in English",
        "impact_category",
        "stage",
        "impact_value",
    ]

    return df[cols]


# ---------------------------------------------------------------------------
# 3. Aggregate to recipe-level impacts
# ---------------------------------------------------------------------------

def compute_recipe_impacts(df_ing):
    """
    Sum across ingredients to get recipe-level impacts:
        - per stage
        - per impact category
        - total per impact category
    """

    # Stage × impact_category breakdown
    df_stage = (
        df_ing.groupby(["impact_category", "stage"])["impact_value"]
        .sum()
        .reset_index()
    )

    # Total per impact category (sum across stages)
    df_total = (
        df_stage.groupby("impact_category")["impact_value"]
        .sum()
        .reset_index()
        .rename(columns={"impact_value": "total_impact"})
    )

    return df_stage, df_total


# ---------------------------------------------------------------------------
# 4. Public pipeline function
# ---------------------------------------------------------------------------

def calculate_baseline(df_mapped):
    """
    Full baseline pipeline:
        1. ingredient-level impacts
        2. recipe-level stage breakdown
        3. recipe-level totals
    """

    df_ing = compute_ingredient_impacts(df_mapped)
    df_stage, df_total = compute_recipe_impacts(df_ing)

    return {
        "ingredient_breakdown": df_ing,
        "stage_breakdown": df_stage,
        "impact_totals": df_total,
    }
