"""
run_model.py

End-to-end pipeline:
    1. Load Agribalyse
    2. Load ingredients
    3. Map ingredients to Agribalyse
    4. Compute baseline impacts
    5. Apply scenarios (optional)
    6. Generate plots (optional)

This is the orchestration layer for the modelling spine.
"""

from src.ingest import load_and_reshape_agribalyse
from src.mapping import load_ingredients, map_ingredients_to_agribalyse
from src.baseline import calculate_baseline
from src.scenario import (
    apply_scenario,
    modify_quantity,
    compare_baseline_vs_scenario,
)
from src.scenario_multipliers import calculate_scenarios
from src.plots import (
    plot_ingredient_breakdown,
    plot_stage_breakdown,
    plot_impact_totals,
    plot_baseline_vs_scenario,
)

import matplotlib.pyplot as plt




def run_pipeline(apply_multiplier_scenarios=False, apply_structural_scenarios=False):
    print("Loading Agribalyse...")
    df_agb = load_and_reshape_agribalyse()

    print("Loading ingredients...")
    df_ing = load_ingredients()

    print("Mapping ingredients...")
    df_mapped = map_ingredients_to_agribalyse(df_ing, df_agb)

    print("Computing baseline impacts...")
    baseline = calculate_baseline(df_mapped)

    # Optional: structural scenarios
    if apply_structural_scenarios:
        print("Applying structural scenario...")
        # Example: reduce beef by 20%
        mods = [
            lambda df: modify_quantity(df, "Beef mince", 200),
        ]
        df_scenario = apply_scenario(df_mapped, mods)
        scenario = calculate_baseline(df_scenario)
        df_delta = compare_baseline_vs_scenario(baseline, scenario)

        print("Plotting baseline vs scenario...")
        fig, ax = plot_baseline_vs_scenario(df_delta)
        plt.show()

    # Optional: multiplier scenarios
    if apply_multiplier_scenarios:
        print("Applying multiplier scenarios...")
        df_scenarios = calculate_scenarios(baseline["impact_totals"])
        print(df_scenarios.head())

    print("Plotting baseline totals...")
    fig, ax = plot_impact_totals(baseline["impact_totals"])
    plt.show()

    print("Done.")


if __name__ == "__main__":
    run_pipeline()
