import os
import requests
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI

from llm_utils import fetch_related_subjects

load_dotenv()


openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

BACKEND_URL: str = "http://localhost:8000"
INITIAL_SUBJECTS: list[str] = ["Artificial Intelligence", "Deep Learning", "Computer Vision"]
NUM_FETCH_RELATED_SUBJECTS: int = 3

@dataclass
class Subject:
    id: int
    name: str

    def from_json_data(json: dict) -> "Subject":
        data = json["data"]
        return Subject(id=data["id"], name=data["name"])
    

@dataclass
class SubjectRelation:
    id: int
    subject_id: int
    related_subject_id: int

    def from_json_data(json: dict) -> "SubjectRelation":
        data = json["data"]
        return SubjectRelation(
            id=data["id"],
            subject_id=data["subject_id"],
            related_subject_id=data["related_subject_id"]
        )


def fetch_subject_by_name(subject_name: str) -> Subject:
    response = requests.get(f"{BACKEND_URL}/subjects?name={subject_name}")
    if response.status_code == 200:
        s = Subject.from_json_data(response.json())
        print(f"Fetched subject: {s}")
        return s
    else:
        raise Exception(f"Failed to fetch subject: {response.json()}")
    

def create_subject(subject_name: str) -> Subject:
    response = requests.post(f"{BACKEND_URL}/subjects", json={"data": {"name": subject_name}})
    if response.status_code == 201:
        s = Subject.from_json_data(response.json())
        print(f"Created subject: {s}")
        return s
    else:
        raise Exception(f"Failed to create subject: {response.json()}")


def find_or_create_subject(subject_name: str) -> Subject:
    try:
        return fetch_subject_by_name(subject_name)
    except Exception as e:
        print(f"Subject {subject_name} not found, creating...")
        return create_subject(subject_name)


def store_subject_relation(subject_id: int, related_subject_id: int):
    response = requests.post(f"{BACKEND_URL}/subject-relations", json={
        "data": {
            "subject_id": subject_id, 
            "related_subject_id": related_subject_id,
        }
    })
    if response.status_code == 201:
        sr = SubjectRelation.from_json_data(response.json())
        print(f"Created subject relation: {sr}")
        return sr
    elif response.status_code == 409:
        print(f"Subject relation already exists: {response.json()}")
        return None
    else:
        raise Exception(f"Failed to create subject relation: {response.json()}")


related_subjects_lookup: dict[str, list[str]] | None = fetch_related_subjects(
    openai_client=openai_client, 
    model_name="gpt-4.1-nano",
    input_subjects=INITIAL_SUBJECTS, 
    num_related_subjects=NUM_FETCH_RELATED_SUBJECTS,
)
if related_subjects_lookup is None:
    raise Exception("Failed to fetch related subjects")


print("-" * 100)
print("Related Subjects Lookup:")
print(related_subjects_lookup)
print("-" * 100)

# create new subjects and subject relations
subject: str
related_subjects: list[str]
for subject_name, related_subject_names in related_subjects_lookup.items():
    print(f"Subject: {subject_name}")
    print(f"Related Subjects: {related_subject_names}")
    print("Storing to backend...")
    s: Subject = find_or_create_subject(subject_name)
    for related_subject_name in related_subject_names:
        related_s = find_or_create_subject(related_subject_name)
        store_subject_relation(s.id, related_s.id)
    print("-" * 100)

