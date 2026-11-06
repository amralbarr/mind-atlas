# Resume Screening & Candidate Matching

## Description
AI that reads resumes/CVs and job descriptions, extracts structured data (skills, experience, education), and scores or ranks candidates against a role's requirements. The AI layer that typically sits inside or alongside an ATS.

## Input
- Resumes/CVs (PDF, DOCX, scanned)
- Job description / requirements

## Output
- Structured candidate profile (skills, years of experience, education, contact info)
- A match score or ranked shortlist against a specific job description

## Related Capabilities
- [RAG](rag-retrieval-augmented-generation.md) — same retrieve+score pattern applied to resumes instead of a document library
- [AI-Driven Interviews](../../multimodal/multimodal-understanding/ai-driven-interviews-chat-voice-video.md) — usually the next step after a candidate passes screening

## Software & Platforms

**Open source:**
- [OpenCATS](../../../tools-platforms/hr-and-recruiting-tools/opencats.md) — self-hosted ATS (parsing/screening is basic; usually paired with a separate parsing API)
- [Resume Matcher](../../../tools-platforms/hr-and-recruiting-tools/resume-matcher.md) — open-source resume-to-job-description scoring

**Paid:**
- [Greenhouse](../../../tools-platforms/hr-and-recruiting-tools/greenhouse.md)
- [Ashby](../../../tools-platforms/hr-and-recruiting-tools/ashby.md)
- [Workable](../../../tools-platforms/hr-and-recruiting-tools/workable.md)
- [Gem](../../../tools-platforms/hr-and-recruiting-tools/gem.md)
- [Textkernel](../../../tools-platforms/hr-and-recruiting-tools/textkernel.md) (formerly Sovren) — the parsing engine behind many ATS products' "AI screening" feature

## Applications
- High-volume applicant triage
- Internal mobility / skills matching
- Candidate ranking for recruiter review

## A note on risk
Automated resume screening and interview scoring face real legal/regulatory scrutiny in several jurisdictions — e.g. NYC Local Law 144 requires an independent bias audit for automated employment-decision tools, and the EU AI Act classifies hiring AI as "high-risk." Document a vendor's compliance/bias-audit posture, not just its accuracy claims.
