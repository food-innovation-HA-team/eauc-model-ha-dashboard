"""
run_model.py

End-to-end pipeline for the EAUC lasagna sustainability model.

This script:
1. Loads and reshapes the Agribalyse dataset
2. Loads and maps recipe ingredients to Agribalyse rows
3. Computes baseline impacts per portion
4. Applies scenario A/B/C modifiers
5. Generates Scenario D (student-facing value)
6. Writes outputs to the outputs/ directory

This is the script colleagues can run without touching any internals.
"""

import pandas as pd
from pathlib import Path

# Import modules from src/
from src.ingest import load_and_reshape_agribalyse
from src.mapping import load_ingredients, map_ingredients_to_agribalyse
from src.baseline import calculate_baseline
from src.scenarios import calculate_scenarios
from src.student_value import get_student_value_scenario


# ---------------------------------------------------------------------------
# OUTPUT DIRECTORY
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------

def run_pipeline():
    print("\n=== EAUC Lasagna Sustainability Model ===\n")

    # 1. Load and reshape Agribalyse
    print("Step 1: Loading Agribalyse...")
    df_agb = load_and_reshape_agribalyse()
    print(f"  ✓ Loaded {len(df_agb):,} tidy rows")

    # 2. Load ingredients
    print("Step 2: Loading ingredients...")
    df_ing = load_ingredients()
    print(f"  ✓ Loaded {len(df_ing)} ingredients")

    # 3. Map ingredients to Agribalyse
    print("Step 3: Mapping ingredients...")
    df_mapped = map_ingredients_to_agribalyse(df_ing, df_agb)
    print(f"  ✓ Mapped to {df_mapped['Product Name in English'].nunique()} Agribalyse products")

    # 4. Compute baseline impacts
    print("Step 4: Computing baseline impacts...")
    df_baseline = calculate_baseline(df_mapped)
    print("  ✓ Baseline impacts computed")

    # 5. Apply scenarios A/B/C
    print("Step 5: Applying scenarios...")
    df_scenarios = calculate_scenarios(df_baseline)
    print("  ✓ Scenario impacts computed")

    # 6. Generate Scenario D narrative
    print("Step 6: Generating student-facing narrative...")
    scenario_d = get_student_value_scenario()
    print("  ✓ Scenario D narrative generated")

    # 7. Write outputs
    print("Step 7: Writing outputs...")

    df_baseline.to_csv(OUTPUT_DIR / "baseline_results.csv", index=False)
    df_scenarios.to_csv(OUTPUT_DIR / "scenario_results.csv", index=False)

    # Write Scenario D as a JSON file
    import json
    with open(OUTPUT_DIR / "scenario_d_narrative.json", "w") as f:
        json.dump(scenario_d, f, indent=4)

    print("  ✓ Outputs written to outputs/ directory")

    print("\n=== Pipeline complete ===\n")


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_pipeline()