from pydantic import BaseModel

class ClauseInput(BaseModel):
    clause_id: str
    compliance_status: str
    evidence: str
    documents: str
    findings: str
    answers: dict  # yes / no / partial
