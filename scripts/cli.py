import os
from dotenv import load_dotenv

from fire import Fire
from openai import OpenAI

from llm_utils import OpenAIModel, SubjectToRelatedSubjects, fetch_related_subjects

load_dotenv()

openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def completion_poc() -> str:
    completion = openai_client.chat.completions.create(
        model=OpenAIModel.GPT_4_1_NANO.value,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"},
        ]
    )
    print(completion.choices[0].message.content)


def fetch_related_subjects_poc() -> str:
    input_subjects = ["quantum physics"]
    print(f"Input subjects: {input_subjects}")
    related_subjects_lookup: list[SubjectToRelatedSubjects] | None = fetch_related_subjects(
        openai_client=openai_client,
        model_name=OpenAIModel.GPT_4_1_NANO.value,
        input_subjects=["quantum physics"],
        num_related_subjects=3,
    )
    print(f"Related subjects lookup: {related_subjects_lookup}")


if __name__ == "__main__":
    Fire({
        "completion_poc": completion_poc,
        "fetch_related_subjects_poc": fetch_related_subjects_poc,
    })
