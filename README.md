# CT-200 QA System

Parses the CardioTrack CT-200 device manual (PDF) into a versioned,
browsable tree, and generates QA test cases via LLM from user-selected
sections, with staleness detection when the document changes.

## Setup

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    copy .env.example .env   # then add your GROQ_API_KEY

## Run

    uvicorn app.main:app --reload

## Test

    python3 -m pytest tests/ -v

## Triggering the v1 -> v2 re-ingestion flow

    curl -X POST "http://127.0.0.1:8000/documents/1/ingest" -F "file=@data/ct200_manual.pdf"
    curl -X POST "http://127.0.0.1:8000/documents/1/ingest" -F "file=@data/ct200_manual_v2.pdf"

## Run the complete demo using Git Bash:

bash scripts/demo_flow.sh


See APPROACH.md for data model, parsing decisions, versioning strategy,
and the decision log.