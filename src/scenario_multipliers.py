"""
scenarios.py

This module applies scenario modifiers (A, B, C) to the baseline impacts
computed in baseline.py.

Inputs:
- df_baseline: dataframe with columns:
      impact_category
      baseline_value_per_portion

- scenario_modifiers.csv:
      scenario, ingredient, GHG, land, water, energy, waste

Outputs:
- df_scenarios: dataframe with columns:
      scenario
      impact_category
      scenario_value_per_portion

Key logic:
1. Load scenario modifiers
2. Convert modifiers to a per-impact-category multiplier
3. Apply multipliers to baseline impacts
4. Return a tidy scenario impact table
"""

import pandas as pd
from pathlib import Path
from config import SCENARIO_MODIFIERS_FILE


# ---------------------------------------------------------------------------
# LOAD SCENARIO MODIFIERS
# ---------------------------------------------------------------------------

def load_scenario_modifiers():
    """
    Load scenario_modifiers.csv.

    Returns
    -------
    df_mod : pandas.DataFrame
        Columns:
            - scenario
            - ingredient
            - GHG
            - land
            - water
            - energy
            - waste
    """
    df_mod = pd.read_csv(SCENARIO_MODIFIERS_FILE)
    return df_mod


# ---------------------------------------------------------------------------
# APPLY SCENARIO MULTIPLIERS
# ---------------------------------------------------------------------------

def apply_scenario(df_baseline, df_mod):
    """
    Apply scenario multipliers to baseline impacts.

    Parameters
    ----------
    df_baseline : pandas.DataFrame
        Columns:
            - impact_category
            - baseline_value_per_portion

    df_mod : pandas.DataFrame
        Scenario modifiers table

    Returns
    -------
    df_scenarios : pandas.DataFrame
        Columns:
            - scenario
            - impact_category
            - scenario_value_per_portion
    """

    # For now, assume each impact category uses the same multiplier column name
    # (GHG, land, water, energy, waste)
    # You can refine this later if you want category-specific logic.

    scenario_frames = []

    for scenario in df_mod["scenario"].unique():
        df_s = df_mod[df_mod["scenario"] == scenario]

        # For now, use the first row (e.g., ALL) as the scenario-wide multiplier
        # This can be extended later to ingredient-specific multipliers.
        row = df_s.iloc[0]

        # Build a dictionary of multipliers
        multipliers = {
            "impact_1": row["GHG"],
            "impact_2": row["land"],
            "impact_3": row["water"],
            "impact_4": row["energy"],
            "impact_5": row["waste"],
            # impacts 6–20 default to 1.0 unless you extend the CSV
        }

        # Apply multipliers
        df_tmp = df_baseline.copy()
        df_tmp["scenario"] = scenario

        df_tmp["scenario_value_per_portion"] = df_tmp.apply(
            lambda r: r["baseline_value_per_portion"] *
                      multipliers.get(r["impact_category"], 1.0),
            axis=1
        )

        scenario_frames.append(df_tmp)

    df_scenarios = pd.concat(scenario_frames, ignore_index=True)
    return df_scenarios


# ---------------------------------------------------------------------------
# PUBLIC PIPELINE FUNCTION
# ---------------------------------------------------------------------------

def calculate_scenarios(df_baseline):
    """
    Full scenario pipeline:
    - Load modifiers
    - Apply to baseline

    Parameters
    ----------
    df_baseline : pandas.DataFrame

    Returns
    -------
    df_scenarios : pandas.DataFrame
    """
    df_mod = load_scenario_modifiers()
    return apply_scenario(df_baseline, df_mod)