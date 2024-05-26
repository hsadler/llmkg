import json

from openai import OpenAI


class OpenAIClient:
    client: OpenAI

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

    def fetch_related_subjects(
        self,
        input_subjects: list[str],
        num_related_subjects: int,
    ) -> dict[str, list[str]]:
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            n=1,
            messages=[
                {
                    "role": "system",
                    "content": """
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
                    """,
                },
                {
                    "role": "user",
                    "content": f"""
                        Give me {num_related_subjects} related subjects for each \
                        subject in the list: {input_subjects} \
                    """,
                },
            ],
        )
        completion_content: str | None = completion.choices[0].message.content
        if completion_content is None:
            raise ValueError("No completion content found in response")
        try:
            response: dict[str, list[str]] = json.loads(completion_content)
            return response
        except json.JSONDecodeError as e:
            raise e
