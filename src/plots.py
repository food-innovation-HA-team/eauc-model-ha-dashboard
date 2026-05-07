import matplotlib.pyplot as plt
import pandas as pd
from style import COLOR_PALETTE

# ---------------------------------------------------------
# Helper: wrap long x‑axis labels
# ---------------------------------------------------------
def wrap_labels(ax, width=12):
    """Wrap long x‑axis labels to avoid overlap."""
    labels = [label.get_text() for label in ax.get_xticklabels()]
    wrapped = ['\n'.join(label[i:i+width] for i in range(0, len(label), width))
               for label in labels]
    ax.set_xticklabels(wrapped)


# ---------------------------------------------------------
# Plot: Impact totals (baseline)
# ---------------------------------------------------------
def plot_impact_totals(df):
    fig, ax = plt.subplots()

    df_sorted = df.sort_values("total_impact", ascending=False)

    ax.bar(
        df_sorted["impact_category"],
        df_sorted["total_impact"],
        color=COLOR_PALETTE
    )

    ax.set_title("Total environmental impacts", pad=15)
    ax.set_xlabel("Impact category")
    ax.set_ylabel("Impact value")

    wrap_labels(ax)
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    fig.tight_layout()
    return fig, ax


# ---------------------------------------------------------
# Plot: Stage‑level breakdown
# ---------------------------------------------------------
def plot_stage_breakdown(df, impact_choice):
    fig, ax = plt.subplots()

    df_sel = df[df["impact_category"] == impact_choice]

    ax.bar(
        df_sel["stage"],
        df_sel["impact_value"],
        color=COLOR_PALETTE
    )

    ax.set_title(f"Stage‑level breakdown: {impact_choice}", pad=15)
    ax.set_xlabel("Stage")
    ax.set_ylabel("Impact value")

    wrap_labels(ax)
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    fig.tight_layout()
    return fig, ax


# ---------------------------------------------------------
# Plot: Ingredient‑level breakdown
# ---------------------------------------------------------
def plot_ingredient_breakdown(df, impact_choice):
    fig, ax = plt.subplots()

    df_sel = df[df["impact_category"] == impact_choice]

    ax.bar(
        df_sel["ingredient"],
        df_sel["impact_value"],
        color=COLOR_PALETTE
    )

    ax.set_title(f"Ingredient contributions: {impact_choice}", pad=15)
    ax.set_xlabel("Ingredient")
    ax.set_ylabel("Impact value")

    wrap_labels(ax)
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    fig.tight_layout()
    return fig, ax


# ---------------------------------------------------------
# Plot: Baseline vs Scenario (or Custom)
# ---------------------------------------------------------
def plot_baseline_vs_scenario(df):
    fig, ax = plt.subplots()

    df_sorted = df.sort_values("baseline_value", ascending=False)

    x = df_sorted["impact_category"]
    baseline_vals = df_sorted["baseline_value"]
    scenario_vals = df_sorted["scenario_value"]

    width = 0.35
    positions = range(len(x))

    ax.bar(
        [p - width/2 for p in positions],
        baseline_vals,
        width=width,
        label="Baseline",
        color=COLOR_PALETTE[0]
    )

    ax.bar(
        [p + width/2 for p in positions],
        scenario_vals,
        width=width,
        label="Scenario",
        color=COLOR_PALETTE[1]
    )

    ax.set_xticks(positions)
    ax.set_xticklabels(x)

    ax.set_title("Baseline vs Scenario", pad=15)
    ax.set_xlabel("Impact category")
    ax.set_ylabel("Impact value")

    wrap_labels(ax)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.legend()

    fig.tight_layout()
    return fig, ax
