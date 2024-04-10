import json

import streamlit as st
import graphviz
from openai import OpenAI

openai_client = OpenAI(
    api_key="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"
)

st.set_page_config(
    page_title="ChatGPT Knowledge Graph",
    page_icon="🧠",
    layout="wide",
)
st.title("ChatGPT Knowledge Graph")

# gather user inputs
initial_subject: str = st.text_input("Subject: ", "")
mode: str = st.selectbox("Mode", ["child learning", "academic research", "casual learning"])
subjects_breadth: int = 3
subjects_depth: int = 4

def fetch_related_subjects(
    input_subjects: list[str], 
    num_related_subjects: int, 
    mode: str,
) -> dict[str, list[str]]:
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
                    \n \
                    Your response should be for the purpose of {mode}. \
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
    related_subjects_lookup: dict[str, list[str]] = json.loads(completion_content)
    return related_subjects_lookup

def construct_knowlege_graph(
    input_subject: str, 
    subject_breadth: int, 
    subject_depth: int,
    mode: str
) -> dict[str, list[str]]:
    def explore_subject_nodes(subjects: list[str], breadth: int) -> dict[str, list[str]]:
        related_subjects_lookup: dict[str, list[str]] = fetch_related_subjects(subjects, breadth, mode)
        return related_subjects_lookup
    knowledge_graph: dict[str, dict[str, bool]] = {}
    latest_recieved_subjects: set[str] = set()
    for i in range(subject_depth): 
        input_subjects: list[str] = [input_subject] if i == 0 else list(latest_recieved_subjects)
        related_subjects_lookup: dict[str, list[str]] = explore_subject_nodes(input_subjects, subject_breadth)
        latest_recieved_subjects = set()
        for subject, related_subjects in related_subjects_lookup.items():
            subject = subject.lower()
            related_subjects = [related_subject.lower() for related_subject in related_subjects]
            latest_recieved_subjects.update(related_subjects)
            if subject not in knowledge_graph:
                knowledge_graph[subject] = {}
            for related_subject in related_subjects:
                knowledge_graph[subject][related_subject] = True
    return knowledge_graph        

# display knowledge graph if initial subject is provided
if initial_subject and mode:
    knowledge_graph: dict[str, dict[str, bool]] = construct_knowlege_graph(
        initial_subject, subjects_breadth, subjects_depth, mode
    )

    graph = graphviz.Digraph(
        name="knowledge_graph",
        format="png", 
        # engine="neato",
        renderer="gd",
        graph_attr={
            "rankdir": "LR",
            "nodesep": "0.5",
            "shape": "box"
            # "ranksep": "2.4",
            # "ranksep": "1",
            # "overlap": "false",
            # "node": "[shape=box]",
            # "size": "10"
        },
        strict=True
    )
    for subject, related_subjects in knowledge_graph.items():
        graph.node(subject)
        for related_subject in related_subjects:
            graph.edge(subject, related_subject)
    st.graphviz_chart(graph, use_container_width=True)
