from openai import OpenAI
from openai.types import ChatModel
from pydantic import BaseModel


class SubjectToRelatedSubjects(BaseModel):
    subject_name: str
    related_subject_names: list[str]


class RelatedSubjectsResponse(BaseModel):
    data: list[SubjectToRelatedSubjects]


def fetch_related_subjects(
    openai_client: OpenAI,
    model_name: ChatModel,
    input_subjects: list[str], 
    num_related_subjects: int, 
) -> list[SubjectToRelatedSubjects] | None:
    completion = openai_client.chat.completions.parse(
        model=model_name,
        n=1,
        messages=[
            {
                "role": "system", 
                "content": '''
                    You are a constructor of knowledge graphs. \
                    The nodes are subjects and the edges are related subjects. \
                    Each subject or related subject should be a simple human readable string. \
                    Keep all strings in the response to 100 characters or less, lowercase, and \
                    without special characters and punctuation.\
                '''
            },
            {
                "role": "user", 
                "content": f'''
                    Give me {num_related_subjects} related subjects for each \
                    subject in the list: {input_subjects} \
                '''
            },
        ],
        response_format=RelatedSubjectsResponse
    )
    related_subjects_response: RelatedSubjectsResponse = completion.choices[0].message.parsed
    return related_subjects_response.data
