def check_compliance(clause_rules, answers):
    missing = []

    for req in clause_rules["mandatory_checks"]:
        if answers.get(req) != "yes":
            missing.append(req)

    return missing
