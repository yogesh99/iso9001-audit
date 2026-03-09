def generate_report_summary(clauses: dict) -> dict:
    summary = {
        "total": 0,
        "Compliant": 0,
        "Minor NC": 0,
        "Major NC": 0,
        "Not Applicable": 0,
        "nc_clauses": []
    }

    for clause_id, data in clauses.items():
        status = data["status"]
        summary["total"] += 1

        if status in summary:
            summary[status] += 1

        if status in ["Minor NC", "Major NC"]:
            summary["nc_clauses"].append(clause_id)

    return summary
