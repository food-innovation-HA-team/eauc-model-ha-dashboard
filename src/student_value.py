"""
student_value.py

Scenario D: Student-facing value.

This module provides structured narrative outputs describing the
non-environmental benefits of the lasagna system improvements.

Scenario D is intentionally non-numerical. It translates the upstream
and downstream improvements (A, B, C) into student-facing value:
- affordability and price stability
- provenance transparency
- learning integration (living laboratory)
- wellbeing and trust
- campus sustainability identity

Outputs are structured dictionaries that can be used in:
- slide decks
- reports
- web interfaces
- dashboards
"""

# ---------------------------------------------------------------------------
# CORE NARRATIVE BLOCKS
# ---------------------------------------------------------------------------

def get_price_stability_block():
    """
    Economic sustainability: price stability and affordability.

    Returns
    -------
    dict
        Structured narrative block.
    """
    return {
        "title": "Stable, Fair Pricing",
        "summary": (
            "Using Future Farm provenance and batch-cooking efficiency reduces "
            "exposure to volatile commodity markets, helping maintain stable, "
            "affordable prices for students."
        ),
        "points": [
            "Reduced dependency on global beef and dairy price swings.",
            "Lower per-portion energy and waste costs through batch cooking.",
            "Predictable pricing supports food security for students."
        ]
    }


def get_provenance_block():
    """
    Social sustainability: provenance transparency and trust.

    Returns
    -------
    dict
    """
    return {
        "title": "Transparent Provenance",
        "summary": (
            "Students gain visibility into where their food comes from, "
            "strengthening trust and connection to the campus food system."
        ),
        "points": [
            "Future Farm provides traceable, high-welfare beef and dairy.",
            "Shorter supply chains increase transparency.",
            "Supports Harper Adams’ identity as a living agricultural campus."
        ]
    }


def get_learning_block():
    """
    Educational sustainability: integration with curriculum.

    Returns
    -------
    dict
    """
    return {
        "title": "Learning Integration",
        "summary": (
            "The lasagna system becomes a teaching asset, linking real campus "
            "operations to sustainability modules, data science, and food systems."
        ),
        "points": [
            "Students can analyse real Agribalyse data and scenario modelling.",
            "Supports experiential learning and applied systems thinking.",
            "Creates opportunities for dissertations, projects, and live case studies."
        ]
    }


def get_wellbeing_block():
    """
    Social sustainability: wellbeing and quality.

    Returns
    -------
    dict
    """
    return {
        "title": "Student Wellbeing",
        "summary": (
            "Higher-quality ingredients and transparent sourcing contribute to "
            "student wellbeing, trust, and satisfaction with campus food."
        ),
        "points": [
            "Fresh, high-quality ingredients from Future Farm.",
            "Reduced waste means fresher batches and better consistency.",
            "Supports a positive campus food culture."
        ]
    }


def get_identity_block():
    """
    Institutional sustainability: campus identity and leadership.

    Returns
    -------
    dict
    """
    return {
        "title": "Campus Sustainability Identity",
        "summary": (
            "The lasagna case study becomes a flagship example of Harper Adams’ "
            "leadership in sustainable food systems."
        ),
        "points": [
            "Demonstrates whole-campus circularity in action.",
            "Provides a narrative for EAUC, REF, and external engagement.",
            "Positions Harper Adams as a national leader in applied sustainability."
        ]
    }


# ---------------------------------------------------------------------------
# PUBLIC PIPELINE FUNCTION
# ---------------------------------------------------------------------------

def get_student_value_scenario():
    """
    Return all Scenario D narrative blocks in a structured format.

    Returns
    -------
    dict
        Keys:
            - price_stability
            - provenance
            - learning
            - wellbeing
            - identity
    """
    return {
        "price_stability": get_price_stability_block(),
        "provenance": get_provenance_block(),
        "learning": get_learning_block(),
        "wellbeing": get_wellbeing_block(),
        "identity": get_identity_block(),
    }