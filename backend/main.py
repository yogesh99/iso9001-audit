import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from services.word_generator import generate_report
from services.narrative_engine import generate_narrative
from services.iso_loader import ISO9001_RULES

app = FastAPI()

# ---------------------------
# CORS (for HTML frontend on Vercel / other origins)
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Generated-Filename"],
)


@app.get("/")
def home():
    return {"status": "ISO 9001 Audit Automation running"}


@app.post("/generate-report")
def generate(audit_data: dict):
    """
    Receives audit input from frontend,
    generates narratives + Word report.
    """

    clauses_payload = {}

    # ---------------------------
    # Process each clause
    # ---------------------------
    for clause_id, data in audit_data.get("clauses", {}).items():

        clause_rules = ISO9001_RULES.get(clause_id)
        if not clause_rules:
            continue

        # ---------------------------
        # System-generated narrative
        # ---------------------------
        answers = data.get("answers", {})
        system_narrative = generate_narrative(
            clause_rules,
            answers
        )

        # ---------------------------
        # Auditor Evidence (VERY IMPORTANT)
        # ---------------------------
        auditor_evidence = (
            data.get("auditor_evidence")
            or data.get("auditorEvidence")
            or ""
        ).strip()

        # ---------------------------
        # Combine evidence correctly
        # ---------------------------
        if auditor_evidence:
            evidence_text = (
                system_narrative
                + "\n\n"
                + "Auditor Evidence (site specific observations):\n"
                + auditor_evidence
            )
        else:
            evidence_text = system_narrative

        # ---------------------------
        # Final clause payload
        # ---------------------------
        clauses_payload[clause_id] = {
            "evidence": evidence_text,
            "documents": data.get("documents", ""),
            "findings": data.get("findings", ""),
            "status": data.get("status", "Compliant")
        }

    # ---------------------------
    # Final audit object
    # ---------------------------
    final_audit_data = {
        "client_name": audit_data.get("client_name", "Demo Client"),
        "audit_type": audit_data.get("audit_type", "Stage 2"),
        "clauses": clauses_payload
    }

    file_path = generate_report(final_audit_data)
    filename = os.path.basename(file_path)

    return FileResponse(
        file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"X-Generated-Filename": filename},
    )
