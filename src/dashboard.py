"""
Harper Adams Catering Sustainability Dashboard
----------------------------------------------

A Streamlit GUI for:
    - Loading a recipe
    - Viewing baseline impacts
    - Viewing stage-level breakdowns
    - Comparing baseline vs scenario
    - Displaying intuitive, colleague-friendly visuals
"""

import os
import re
import io
import streamlit as st
import matplotlib.pyplot as plt

from ingest import load_and_reshape_agribalyse
from mapping import load_ingredients, map_ingredients_to_agribalyse
from baseline import calculate_baseline
from scenario import apply_scenario, modify_quantity
from plots import (
    plot_ingredient_breakdown,
    plot_stage_breakdown,
    plot_impact_totals,
    plot_baseline_vs_scenario,
)

print("STREAMLIT WORKING DIR:", os.getcwd())


# ---------------------------------------------------------------------------
# GLOBAL PLOT STYLE
# ---------------------------------------------------------------------------

plt.style.use("default")

CUSTOM_STYLE = {
    "axes.titlesize": 16,
    "axes.labelsize": 14,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12,
    "figure.figsize": (8, 5),
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.spines.top": False,
    "axes.spines.right": False,
}

plt.rcParams.update(CUSTOM_STYLE)


def fig_to_png_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)
    return buf


# ---------------------------------------------------------------------------
# LOAD DATA ONCE
# ---------------------------------------------------------------------------

@st.cache_data
def load_data():
    df_agb = load_and_reshape_agribalyse()
    df_ing = load_ingredients()
    df_mapped = map_ingredients_to_agribalyse(df_ing, df_agb)
    baseline = calculate_baseline(df_mapped)
    return df_agb, df_ing, df_mapped, baseline


# ---------------------------------------------------------------------------
# STREAMLIT APP
# ---------------------------------------------------------------------------

def main():
    st.title("Harper Adams Catering Sustainability Dashboard")
    st.markdown("### Evidence-based environmental insights for catering decisions")

    df_agb, df_ing, df_mapped, baseline = load_data()

    # Map internal impact category codes to human-readable labels
    impact_label_map = {
        "impact_1": "Climate change",
        "impact_2": "Water use",
        "impact_3": "Land use",
        "impact_4": "Eutrophication potential",
        "impact_5": "Acidification potential",
    }

    for key in ["impact_totals", "stage_breakdown", "ingredient_breakdown"]:
        if "impact_category" in baseline[key].columns:
            baseline[key] = baseline[key].copy()
            baseline[key]["impact_category"] = (
                baseline[key]["impact_category"].replace(impact_label_map)
            )

    allowed_impacts = list(impact_label_map.values())

    for key in ["impact_totals", "stage_breakdown", "ingredient_breakdown"]:
        if "impact_category" in baseline[key].columns:
            baseline[key] = baseline[key][
                baseline[key]["impact_category"].isin(allowed_impacts)
            ]

    # -------------------------
    # Baseline view
    # -------------------------
    st.header("Baseline Impacts")
    st.write("These are the environmental impacts of the current recipe.")

    fig, ax = plot_impact_totals(baseline["impact_totals"])
    st.pyplot(fig)
    st.download_button(
        "Download figure as PNG",
        fig_to_png_bytes(fig),
        "baseline_impacts.png",
    )

    # -------------------------
    # Stage breakdown
    # -------------------------
    st.header("Stage-Level Breakdown")
    impact_choice = st.selectbox(
        "Choose an impact category",
        baseline["impact_totals"]["impact_category"].unique()
    )

    fig, ax = plot_stage_breakdown(baseline["stage_breakdown"], impact_choice)
    st.pyplot(fig)
    st.download_button(
        "Download figure as PNG",
        fig_to_png_bytes(fig),
        "stage_breakdown.png",
    )

    # -------------------------
    # Ingredient breakdown
    # -------------------------
    st.header("Ingredient Contributions")
    fig, ax = plot_ingredient_breakdown(
        baseline["ingredient_breakdown"],
        impact_choice
    )
    st.pyplot(fig)
    st.download_button(
        "Download figure as PNG",
        fig_to_png_bytes(fig),
        "ingredient_breakdown.png",
    )

    # -------------------------
    # Build your own lasagna
    # -------------------------
    st.header("Build your own lasagna")
    st.write("Adjust ingredient quantities to see how your recipe affects environmental impacts.")

    custom_quantities = {}
    for _, row in df_ing.iterrows():
        ing_name = row["ingredient"]
        default_qty = row["quantity_g"]

        try:
            default_qty_num = int(float(str(default_qty)))
        except ValueError:
            default_qty_num = 0

        custom_quantities[ing_name] = st.number_input(
            f"{ing_name} (g)", min_value=0, max_value=2000, value=default_qty_num, step=1
        )

    if st.button("Recalculate impacts for my lasagna"):
        df_ing_custom = df_ing.copy()
        df_ing_custom["quantity_g"] = df_ing_custom["ingredient"].map(custom_quantities)

        df_mapped_custom = map_ingredients_to_agribalyse(df_ing_custom, df_agb)
        baseline_custom = calculate_baseline(df_mapped_custom)

        for key in ["impact_totals", "stage_breakdown", "ingredient_breakdown"]:
            if "impact_category" in baseline_custom[key].columns:
                baseline_custom[key] = baseline_custom[key][
                    baseline_custom[key]["impact_category"].isin(allowed_impacts)
                ]

        st.subheader("Environmental impacts of your lasagna")

        impact_choice_custom = st.selectbox(
            "Choose an impact category for your lasagna",
            allowed_impacts,
            key="impact_choice_custom"
        )

        fig, ax = plot_ingredient_breakdown(
            baseline_custom["ingredient_breakdown"],
            impact_choice_custom
        )
        st.pyplot(fig)
        st.download_button(
            "Download figure as PNG",
            fig_to_png_bytes(fig),
            "custom_ingredients.png",
        )

        fig, ax = plot_stage_breakdown(
            baseline_custom["stage_breakdown"],
            impact_choice_custom
        )
        st.pyplot(fig)
        st.download_button(
            "Download figure as PNG",
            fig_to_png_bytes(fig),
            "custom_stages.png",
        )

        st.subheader("Comparison: Original baseline vs your lasagna")

        df_delta_custom = baseline_custom["impact_totals"].merge(
            baseline["impact_totals"],
            on="impact_category",
            suffixes=("_custom", "_baseline")
        )
        df_delta_custom["change"] = (
            df_delta_custom["total_impact_custom"] - df_delta_custom["total_impact_baseline"]
        )

        fig, ax = plot_baseline_vs_scenario(
            df_delta_custom.rename(columns={
                "total_impact_baseline": "baseline_value",
                "total_impact_custom": "scenario_value",
                "change": "change_absolute"
            })
        )
        st.pyplot(fig)
        st.download_button(
            "Download figure as PNG",
            fig_to_png_bytes(fig),
            "custom_vs_baseline.png",
        )

    # ----------------------------------------
    # Scenario Explorer
    # ----------------------------------------
    st.header("Scenario Explorer")

    ingredient_choice = st.selectbox(
        "Choose an ingredient to modify",
        df_ing["ingredient"].unique()
    )

    raw_val = df_ing.loc[df_ing["ingredient"] == ingredient_choice, "quantity_g"].iloc[0]
    clean_val = re.sub(r"[^0-9.\-]", "", str(raw_val).replace("g", "").strip())
    value = int(float(clean_val)) if clean_val else 0

    new_qty = st.slider("New quantity (g)", min_value=0, max_value=500, value=value)

    if st.button("Apply Scenario"):
        mods = [lambda df: modify_quantity(df, ingredient_choice, new_qty)]
        df_scenario = apply_scenario(df_mapped, mods)
        scenario = calculate_baseline(df_scenario)

        df_delta = scenario["impact_totals"].merge(
            baseline["impact_totals"],
            on="impact_category",
            suffixes=("_scenario", "_baseline")
        )
        df_delta["change"] = (
            df_delta["total_impact_scenario"] - df_delta["total_impact_baseline"]
        )

        fig, ax = plot_baseline_vs_scenario(
            df_delta.rename(columns={
                "total_impact_baseline": "baseline_value",
                "total_impact_scenario": "scenario_value",
                "change": "change_absolute"
            })
        )
        st.pyplot(fig)
        st.download_button(
            "Download figure as PNG",
            fig_to_png_bytes(fig),
            "scenario.png",
        )


if __name__ == "__main__":
    main()
