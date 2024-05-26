import requests
from requests.models import Response
from script_utils import setup_path

setup_path()

from app.clients.openai_client import OpenAIClient

# script to populate the database with subjects and relationships

openai_client = OpenAIClient(api_key="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")
backend_url = "http://localhost:8000"
create_subject_url = f"{backend_url}/api/subjects/related-subjects"

# fetch related subjects for a given subject
subj_to_related_subjects = openai_client.fetch_related_subjects(
    input_subjects=["skateboarding", "fishing", "technology"],
    num_related_subjects=3,
)

for subject, related_subjects in subj_to_related_subjects.items():
    res: Response = requests.post(
        create_subject_url,
        json={
            "subject_name": subject,
            "related_subject_names": related_subjects,
        },
    )
    if res.status_code == 201:
        print(f"Created subject {subject} with related subjects {related_subjects}")
    else:
        print(res.text)
