import json

import streamlit as st
import graphviz
from openai import OpenAI

client = OpenAI(
    api_key="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"
)

st.title("ChatGPT Knowledge Graph")
initial_subject: str = st.text_input("Subject: ", "")
subjects_breadth: int = 4
subjects_depth: int = 4

def get_related_subjects(subject: str, num_related_subjects: int) -> list[str]:
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
    related_subjects: list[str] = json.loads(res_message).keys()
    return related_subjects


if initial_subject:
    related_subjects: list[str] = get_related_subjects(initial_subject, subjects_breadth)

    graph = graphviz.Digraph()
    for r_subject in related_subjects:
        graph.edge(initial_subject, r_subject)

        # related_subjects_2: list[str] = get_related_subjects(r_subject, subjects_breadth)
        # for r_subject_2 in related_subjects_2:
        #     graph.edge(r_subject, r_subject_2)

            # related_subjects_3: list[str] = get_related_subjects(r_subject_2, num_related_subjects)
            # for r_subject_3 in related_subjects_3:
            #     graph.edge(r_subject_2, r_subject_3)

    st.graphviz_chart(graph)


