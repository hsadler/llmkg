from openai import OpenAI

client = OpenAI(
    api_key="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"
)

subject = input("Subject: ")
# num_related_subjects = input("Number of related subjects: ")
num_related_subjects: int = 10

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    n=1,
    messages=[
        {"role": "system", "content": "You are a constructor of knowledge graphs."},
        {"role": "user", "content": 
            f'''
                Give me {num_related_subjects} related subjects to "{subject}" \
                in a json dictionary format like this: \
                ["subject1": 0.543, "subject2": 0.711, "subject3": 0.245] \
                Score each subject with a floating point number from 0 to 1 where \
                the score represents the relevance of the subject to the original subject. \
                The floating point should have 3 decimal places. \
                For example, if the subject is "computing" and the related subjects are \
                "programming", "algorithms", and "data structures", the json dictionary \
                should look like this: \
                ["programming": 0.543, "algorithms": 0.711, "data structures": 0.245]
            '''
        },
    ]
)

res_message: str = completion.choices[0].message.content

print(res_message)
