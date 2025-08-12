import os
import requests
from dataclasses import dataclass
from time import sleep

from dotenv import load_dotenv
from openai import OpenAI

from llm_utils import fetch_related_subjects, SubjectToRelatedSubjects

load_dotenv()


openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

KG_VERSION: str = "2"

BACKEND_URL: str = "http://localhost:8000"
INITIAL_SUBJECTS: list[str] = [
    "science",
    "mathematics",
    "technology",
    "history",
    "literature",
    "language",
    "art",
    "engineering",
    "philosophy",
    "sociology",
    "politics",
    "economics",
    "religion",
    "education",
    "law",
]

SUBJ_NUM_FETCH_RELATED: int = 5
SUBJ_CHUNK_SIZE: int = 30
SUBJ_MAX_DEPTH_LEVEL: int = 10

@dataclass
class Subject:
    id: str
    name: str

    def from_json_data(json: dict) -> "Subject":
        data = json["data"]
        return Subject(id=data["id"], name=data["name"])


@dataclass
class SubjectRelation:
    subject_id: str
    related_subject_id: str

    def from_json_data(json: dict) -> "SubjectRelation":
        data = json["data"]
        return SubjectRelation(
            subject_id=data["subject_id"],
            related_subject_id=data["related_subject_id"]
        )


def fetch_subject_by_name(kg_version: str, subject_name: str) -> Subject:
    response = requests.get(f"{BACKEND_URL}/subjects?name={subject_name}&kg_version={kg_version}")
    if response.status_code == 200:
        s = Subject.from_json_data(response.json())
        print(f"Fetched subject: {s}")
        return s
    else:
        raise Exception(f"Failed to fetch subject: {response.json()}")
    

def create_subject(kg_version: str, subject_name: str) -> Subject:
    response = requests.post(f"{BACKEND_URL}/subjects", json={"data": {"name": subject_name}, "kg_version": kg_version})
    if response.status_code == 201:
        s = Subject.from_json_data(response.json())
        print(f"Created subject: {s}")
        return s
    else:
        raise Exception(f"Failed to create subject: {response.json()}")


def find_or_create_subject(kg_version: str, subject_name: str) -> Subject:
    sleep(0.05)
    try:
        return fetch_subject_by_name(kg_version, subject_name)
    except Exception as e:
        print(f"Subject {subject_name} not found, creating...")
        return create_subject(kg_version, subject_name)


def store_subject_relation(kg_version: str, subject_id: str, related_subject_id: str):
    sleep(0.05)
    response = requests.post(f"{BACKEND_URL}/subject-relations", json={
        "data": {
            "subject_id": subject_id, 
            "related_subject_id": related_subject_id,
        },
        "kg_version": kg_version,
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


def populate_related_subjects(kg_version: str, input_subjects: list[str], level: int) -> list[str]:
    res: list[SubjectToRelatedSubjects] | None = fetch_related_subjects(
        openai_client=openai_client, 
        model_name="gpt-4.1-nano",
        input_subjects=input_subjects, 
        num_related_subjects=SUBJ_NUM_FETCH_RELATED,
    )
    print("-" * 100)
    print(f"Level {level}")
    visited_subjects: set[str] = set()
    subject_to_related_subjects: SubjectToRelatedSubjects
    for subject_to_related_subjects in res:
        subject_name: str = subject_to_related_subjects.subject_name
        related_subject_names: list[str] = subject_to_related_subjects.related_subject_names
        print(f"Subject: {subject_name}")
        print(f"Related Subjects: {related_subject_names}")
        print("Storing to backend...")
        s: Subject = find_or_create_subject(kg_version, subject_name)
        visited_subjects.add(subject_name)
        for related_subject_name in related_subject_names:
            related_s = find_or_create_subject(kg_version, related_subject_name)
            visited_subjects.add(related_subject_name)
            store_subject_relation(kg_version, s.id, related_s.id)
        print("-" * 100)
    print("-" * 100)
    return list(visited_subjects)


if __name__ == "__main__":
    current_level = 0
    current_subjects: list[str] = INITIAL_SUBJECTS
    next_subjects: list[str] = []
    visited_subjects: set[str] = set()
    while current_level < SUBJ_MAX_DEPTH_LEVEL:
        all_next_subjects = []
        for i in range(0, len(current_subjects), SUBJ_CHUNK_SIZE):
            chunk = current_subjects[i:i + SUBJ_CHUNK_SIZE]
            print(f"Processing level {current_level} chunk {i//SUBJ_CHUNK_SIZE + 1}: {chunk}")
            chunk_next_subjects = populate_related_subjects(KG_VERSION, chunk, current_level)
            all_next_subjects.extend(chunk_next_subjects)
        next_subjects = all_next_subjects
        visited_subjects.update(next_subjects)
        current_subjects = next_subjects
        current_level += 1
