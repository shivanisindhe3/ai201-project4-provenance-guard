def combine_scores(llm_score, heuristic_score):
    """
    Combines two AI-likeness scores into one final score.
    0.0 = very human-like
    1.0 = very AI-like
    """
    combined_score = (0.60 * llm_score) + (0.40 * heuristic_score)
    return round(combined_score, 2)