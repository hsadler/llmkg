import json

from openai import OpenAI


def fetch_related_subjects(
    openai_client: OpenAI,
    input_subjects: list[str], 
    num_related_subjects: int, 
) -> dict[str, list[str]] | None:
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        n=1,
        messages=[
            {
                "role": "system", 
                "content": '''
                    You are a constructor of knowledge graphs. \
                    Always provide JSON as a response in the format: \
                    {"subject1": ["related_subject1", "related_subject2", "related_subject3"], \
                    "subject2": ["related_subject1", "related_subject2", "related_subject3"], \
                    "subject3": ["related_subject1", "related_subject2", "related_subject3"]} \
                    \n \
                    Each subject or related subject should be a human readable string. \
                    An example reponse to input subjects ["computing", "cooking"] \
                    would be: \
                    {"computing": ["programming", "algorithms", "data structures"], \
                    "cooking": ["baking", "grilling", "sous vide"]} \
                '''
            },
            {
                "role": "user", 
                "content": f'''
                    Give me {num_related_subjects} related subjects for each \
                    subject in the list: {input_subjects} \
                '''
            },
        ]
    )
    completion_content: str = completion.choices[0].message.content
    try:
        related_subjects_lookup: dict[str, list[str]] = json.loads(completion_content)
        return related_subjects_lookup
    except json.JSONDecodeError:
        print(f"Invalid JSON response from the model: {completion_content}")
        return None
