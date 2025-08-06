import os

from dotenv import load_dotenv
from openai import OpenAI

from llm_utils import fetch_related_subjects

load_dotenv()


openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

related_subjects_lookup: dict[str, list[str]] | None = fetch_related_subjects(
    openai_client, 
    ["Artificial Intelligence", "Deep Learning", "Computer Vision"], 
    3,
)
print(related_subjects_lookup)
