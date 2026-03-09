def generate_narrative(clause_rules: dict, answers: dict) -> str:
    """
    Builds clause narrative using rule-based ISO wording.
    """
    paragraphs = []

    narrative_rules = clause_rules.get("narrative_rules", {})

    for key, answer in answers.items():
        rule = narrative_rules.get(key)

        if not rule:
            continue

        text = rule.get(answer)
        if text:
            paragraphs.append(text)

    return " ".join(paragraphs)
