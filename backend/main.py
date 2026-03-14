import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Ensure imports work when running `uvicorn backend.main:app` from project root
from backend.services.word_generator import generate_report
from backend.services.narrative_engine import generate_narrative
from backend.services.iso_loader import ISO9001_RULES

app = FastAPI()

# ---------------------------
# CORS (for HTML frontend on Vercel / other origins)
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # must be False when allow_origins=["*"] per CORS spec
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
    try:
        clauses_payload = {}

        # ---------------------------
        # Process each clause
        # ---------------------------
        for clause_id, data in audit_data.get("clauses", {}).items():

            clause_rules = ISO9001_RULES.get(clause_id)

            # ---------------------------
            # System-generated narrative (if rules exist)
            # ---------------------------
            answers = data.get("answers", {})
            if clause_rules:
                system_narrative = generate_narrative(
                    clause_rules,
                    answers
                )
            else:
                # No configured rules for this clause – still include auditor evidence
                system_narrative = ""

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
            # If the auditor has entered their own evidence, prefer ONLY that text
            # (the template already adds the "Evidences and comments on conformance:" heading).
            if auditor_evidence:
                evidence_text = auditor_evidence
            else:
                # Fall back to the system-generated narrative when no auditor text is provided.
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
