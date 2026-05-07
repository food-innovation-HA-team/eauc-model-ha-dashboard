"""
scenario.py

Scenario engine for modifying recipe ingredients and recomputing impacts.

This module provides:
    - A clean structure for defining scenario modifications
    - Functions to apply those modifications to the mapped dataframe
    - A comparison function to compute deltas vs baseline

Scenarios operate on the *mapped* dataframe (ingredient × stage × impact_category).
"""

import pandas as pd
from src.baseline import calculate_baseline

# ---------------------------------------------------------------------------
# 1. Scenario modification functions
# ---------------------------------------------------------------------------

def modify_quantity(df, ingredient, new_quantity_g):
    """
    Modify the quantity (in grams) of a given ingredient in the mapped dataframe.

    This is designed to be robust to messy quantity inputs (e.g. '120 g', ' 200',
    or values that arrived as strings via Arrow-backed dataframes).
    """
    df = df.copy()

    # Ensure quantity_g is numeric and robust to messy strings
    df["quantity_g"] = pd.to_numeric(
        df["quantity_g"]
        .astype(str)
        .str.replace(r"[^0-9.\-]", "", regex=True),
        errors="coerce",
    ).fillna(0.0)

    # Assign the new quantity (as float for consistency)
    df.loc[df["ingredient"] == ingredient, "quantity_g"] = float(new_quantity_g)

    return df


def substitute_ingredient(df_mapped, old_name, new_name):
    """
    Replace the Agribalyse product for a given ingredient.
    Assumes the mapping layer will be rerun afterwards.
    """
    df = df_mapped.copy()
    df.loc[df["ingredient"] == old_name, "agribalyse_name"] = new_name
    return df


def remove_ingredient(df_mapped, ingredient):
    """
    Remove an ingredient entirely.
    """
    return df_mapped[df_mapped["ingredient"] != ingredient].copy()


def add_ingredient(df_mapped, ingredient, quantity_g, agribalyse_name):
    """
    Add a new ingredient to the recipe.

    Note: this assumes downstream code either:
      - only needs these three columns, or
      - will re-map / re-augment this row before impact calculation.
    """
    df = df_mapped.copy()

    new_row = {
        "ingredient": ingredient,
        "quantity_g": quantity_g,
        "agribalyse_name": agribalyse_name,
    }

    df_new = pd.DataFrame([new_row])
    df_out = pd.concat([df, df_new], ignore_index=True)

    return df_out


# ---------------------------------------------------------------------------
# 2. Scenario application wrapper
# ---------------------------------------------------------------------------

def apply_scenario(df_mapped, modifications):
    """
    Apply a list of modification functions to the mapped dataframe.

    Parameters
    ----------
    df_mapped : DataFrame
        Output of mapping.map_ingredients_to_agribalyse()
    modifications : list of callables
        Each function takes a DataFrame and returns a modified DataFrame

    Returns
    -------
    df_scenario : DataFrame
        Modified mapped dataframe
    """
    df = df_mapped.copy()

    for fn in modifications:
        out = fn(df)
        if not isinstance(out, pd.DataFrame):
            raise TypeError(
                f"Scenario function {getattr(fn, '__name__', fn)} "
                "did not return a pandas DataFrame."
            )
        df = out

    return df


# ---------------------------------------------------------------------------
# 3. Scenario comparison
# ---------------------------------------------------------------------------

def compare_baseline_vs_scenario(baseline, scenario):
    """
    Compare baseline and scenario impact totals.

    Parameters
    ----------
    baseline : dict
        Output of baseline.calculate_baseline()
    scenario : dict
        Output of baseline.calculate_baseline() on modified data

    Returns
    -------
    df_delta : DataFrame
        Columns:
            impact_category
            baseline_value
            scenario_value
            change_absolute
            change_percent
    """

    df_b = baseline["impact_totals"].rename(
        columns={"total_impact": "baseline_value"}
    )
    df_s = scenario["impact_totals"].rename(
        columns={"total_impact": "scenario_value"}
    )

    df = df_b.merge(df_s, on="impact_category", how="outer").fillna(0)

    df["change_absolute"] = df["scenario_value"] - df["baseline_value"]
    df["change_percent"] = (
        100 * df["change_absolute"] /
        df["baseline_value"].replace(0, pd.NA)
    ).fillna(0)

    return df
