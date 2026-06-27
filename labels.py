def get_attribution(combined_score):
    if combined_score >= 0.75:
        return "likely_ai"
    elif combined_score <= 0.39:
        return "likely_human"
    else:
        return "uncertain"


def get_transparency_label(attribution):
    labels = {
        "likely_ai": (
            "Likely AI-generated. Our system found strong signals that this content "
            "may have been created with AI. This label is based on writing patterns "
            "and confidence scoring, and the creator may appeal this decision."
        ),
        "uncertain": (
            "Uncertain. Our system could not confidently determine whether this content "
            "was written by a human or generated with AI. This content may need manual review."
        ),
        "likely_human": (
            "Likely human-written. Our system found writing patterns that are more "
            "consistent with human-authored content. This label is an estimate, not a guarantee."
        ),
    }

    return labels.get(attribution, labels["uncertain"])